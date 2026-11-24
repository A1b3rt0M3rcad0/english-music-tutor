"""Evidence-based mastery; never infer mastery from a note or a song count."""
from __future__ import annotations

from datetime import date, datetime
from hashlib import sha256
from pathlib import Path

from .store import read_json, write_json, read_yaml, now, slug, require_workspace

TYPES = ('vocabulary', 'expression', 'phrasal_verb', 'idiom', 'grammar',
         'collocation', 'sentence_structure')
STAGES = ('introduced', 'understood', 'practicing', 'acquired', 'consolidated')
MODES = ('comprehension', 'application', 'transfer', 'review')
ASSISTANCE = ('independent', 'assisted', 'unknown')
OUTCOMES = ('correct', 'incorrect', 'not_observed', 'not_assessed')


def path(base: Path) -> Path:
    return base / 'data/knowledge/items.json'


def items(base: Path) -> dict:
    return read_json(path(base), {})


def _policy(base: Path) -> dict:
    cfg = read_yaml(base / 'config.yaml').get('mastery', {})
    result = {'independent_contexts': 2, 'consolidation_reviews': 3,
              'consolidation_days': 14, 'regression_failures': 1}
    result.update({k: cfg[k] for k in result if k in cfg})
    for key, value in result.items():
        if type(value) is not int or not 1 <= value <= 365:
            raise ValueError(f'mastery.{key}: inteiro entre 1 e 365')
    return result


def introduce(base: Path, kind: str, content: str, meaning: str, *,
              sense: str = '', song_id: str | None = None,
              note_id: str | None = None) -> dict:
    require_workspace(base)
    if kind not in TYPES or not content.strip() or not meaning.strip():
        raise ValueError('Tipo válido, conteúdo e significado são obrigatórios')
    if song_id and not (base / 'data/songs' / song_id / 'cycle.json').is_file():
        raise ValueError('Música não encontrada')
    if song_id and (Path(song_id).name != song_id or song_id in ('.', '..')):
        raise ValueError('Identificador de música inválido')
    all_items = items(base)
    identity = '|'.join([kind, ' '.join(content.casefold().split()),
                         ' '.join((sense or meaning).casefold().split())])
    identifier = f'{kind}/{slug(content)}-{sha256(identity.encode()).hexdigest()[:12]}'
    if note_id:
        matches = [x for x in all_items.values() if x.get('note_id') == note_id]
        if matches:
            candidate = matches[0]
            if candidate['content'].casefold().strip() == content.casefold().strip():
                identifier = candidate['id']
        elif note_id in all_items:
            identifier = note_id
    item = all_items.get(identifier)
    if item is None:
        item = {'id': identifier, 'type': kind, 'content': content.strip(),
                'meaning': meaning.strip(), 'sense': sense.strip(),
                'introduced_at': now(), 'status': 'introduced',
                'source_songs': [], 'attempts': [], 'note_id': note_id}
    elif note_id and not item.get('note_id'):
        item['note_id'] = note_id
    if song_id and song_id not in item['source_songs']:
        item['source_songs'].append(song_id)
    all_items[identifier] = item
    write_json(path(base), all_items)
    return item


def get(base: Path, knowledge_id: str) -> dict:
    item = items(base).get(knowledge_id)
    if item is None:
        raise ValueError('Conhecimento não encontrado')
    return item


def _derive(item: dict, policy: dict) -> str:
    stage = 'introduced'
    contexts = set()
    review_days = set()
    failures = 0
    introduced = date.fromisoformat(item['introduced_at'][:10])
    acquired_on = None
    for a in item['attempts']:
        if a['outcome'] not in ('correct', 'incorrect'):
            continue
        if a['outcome'] == 'incorrect':
            if a['assistance'] != 'independent':
                continue
            failures += 1
            if failures >= policy['regression_failures']:
                if stage in ('acquired', 'consolidated'):
                    stage = 'practicing'
                    contexts.clear()
                    review_days.clear()
                    acquired_on = None
                failures = 0
            continue
        if a['assistance'] == 'unknown':
            continue
        failures = 0
        if stage == 'introduced':
            stage = 'understood'
        if a['mode'] == 'comprehension':
            continue
        if STAGES.index(stage) < STAGES.index('practicing'):
            stage = 'practicing'
        if a['assistance'] != 'independent':
            continue
        day = date.fromisoformat(a['at'][:10])
        if a['mode'] in ('transfer', 'review'):
            contexts.add(' '.join(a['context'].casefold().split()))
        if stage == 'practicing' and len(contexts) >= policy['independent_contexts']:
            stage = 'acquired'
            acquired_on = day
        if (a['mode'] == 'review' and stage in ('acquired', 'consolidated')
                and acquired_on is not None and day > acquired_on):
            review_days.add(day)
            if (len(review_days) >= policy['consolidation_reviews']
                    and (day - introduced).days >= policy['consolidation_days']):
                stage = 'consolidated'
    return stage


def record(base: Path, knowledge_id: str, attempt_id: str, mode: str,
           outcome: str, assistance: str, context: str, question: str,
           answer: str, feedback: str, *, song_id: str | None = None,
           at: str | None = None) -> dict:
    if mode not in MODES or outcome not in OUTCOMES or assistance not in ASSISTANCE:
        raise ValueError('Modo, resultado ou assistência inválidos')
    if not all(isinstance(x, str) and x.strip() for x in
               (attempt_id, context, question, feedback)):
        raise ValueError('ID, contexto, questão e feedback obrigatórios')
    if outcome in ('correct', 'incorrect', 'not_observed') and not answer.strip():
        raise ValueError('Resposta real obrigatória')
    if song_id and (Path(song_id).name != song_id or song_id in ('.', '..')
                    or not (base / 'data/songs' / song_id / 'cycle.json').is_file()):
        raise ValueError('Música inválida')
    all_items = items(base)
    item = all_items.get(knowledge_id)
    if item is None:
        raise ValueError('Conhecimento não encontrado')
    payload = {'id': attempt_id, 'mode': mode, 'outcome': outcome,
               'assistance': assistance, 'context': context, 'question': question,
               'answer': answer, 'feedback': feedback, 'song_id': song_id}
    for old in item['attempts']:
        if old['id'] == attempt_id:
            if any(old.get(k) != v for k, v in payload.items()):
                raise ValueError('ID de tentativa já utilizado com outros dados')
            return item
        if (outcome == 'correct' and old['outcome'] == 'correct'
                and old['mode'] == mode and old['context'].casefold().strip() == context.casefold().strip()
                and old['question'].casefold().strip() == question.casefold().strip()
                and mode != 'review'):
            raise ValueError('Não duplique a mesma evidência de sucesso')
    timestamp = at or now()
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        raise ValueError('Data da tentativa precisa de fuso')
    if timestamp < item['introduced_at'] or (item['attempts'] and timestamp < item['attempts'][-1]['at']):
        raise ValueError('Tentativa anterior ao histórico')
    item['attempts'].append(dict(payload, at=timestamp))
    if song_id and song_id not in item['source_songs']:
        item['source_songs'].append(song_id)
    item['status'] = _derive(item, _policy(base))
    write_json(path(base), all_items)
    return item


def summary(base: Path) -> dict:
    values = list(items(base).values())
    counts = {stage: sum(x['status'] == stage for x in values) for stage in STAGES}
    return {'total': len(values), 'by_status': counts,
            'acquired_total': counts['acquired'] + counts['consolidated'],
            'expressions_acquired': sum(x['type'] in ('expression', 'phrasal_verb', 'idiom', 'collocation')
                                        and x['status'] in ('acquired', 'consolidated') for x in values)}


def gaps(base: Path) -> list[dict]:
    return [x for x in items(base).values() if x['status'] not in ('acquired', 'consolidated')]


def legacy_note(base: Path, note: dict, meaning: str = '') -> dict | None:
    if note.get('type') not in ('expression', 'grammar'):
        return None
    all_items = items(base)
    note_id = note['id']
    if note_id in all_items:
        item = all_items[note_id]
    else:
        item = next((x for x in all_items.values() if x.get('note_id') == note_id), None)
    if item is None:
        content = note['title']
        candidates = [x for x in all_items.values() if x['content'].casefold().strip() == content.casefold().strip()
                      and x['type'] == note['type'] and not x.get('note_id')]
        if len(candidates) == 1:
            item = candidates[0]
            item['note_id'] = note_id
        else:
            item = {'id': note_id, 'type': note['type'], 'content': content,
                    'meaning': meaning or 'Consulte a nota original',
                    'sense': '', 'introduced_at': note.get('updated_at') or now(),
                    'status': 'introduced', 'source_songs': [], 'attempts': [], 'note_id': note_id}
    if note.get('latest_song') and note['latest_song'] not in item['source_songs']:
        item['source_songs'].append(note['latest_song'])
    all_items[item['id']] = item
    write_json(path(base), all_items)
    return item
