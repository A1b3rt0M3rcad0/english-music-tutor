"""Evidence-linked revision scheduling for schema 2."""
from datetime import date, timedelta
from .store import read_json, write_json, read_yaml, today, now
from . import mastery


def _path(base):
    return base / 'data/reviews.json'


def _policy(base):
    cfg = read_yaml(base / 'config.yaml')
    initial = cfg['method']['review_intervals_days']
    policy = cfg.get('review_policy', {})
    maintenance = policy.get('maintenance_days', [60, 90, 120, 180])
    for sequence in (initial, maintenance):
        if not sequence or any(type(n) is not int or n <= 0 for n in sequence) or sorted(set(sequence)) != sequence:
            raise ValueError('Intervalos de revisão precisam ser positivos e crescentes')
    if type(policy.get('maintenance_enabled', True)) is not bool:
        raise ValueError('maintenance_enabled deve ser booleano')
    return initial, maintenance, policy.get('maintenance_enabled', True)


def schedule(base, knowledge_id, song_id=None):
    initial, _, enabled = _policy(base)
    item = mastery.get(base, knowledge_id)
    queue = read_json(_path(base), {})
    # Preserve the keys of the old note-based queue.
    key = item.get('note_id') or knowledge_id
    existing_key = next((k for k, v in queue.items() if v.get('knowledge_id') == knowledge_id), key)
    row = queue.get(existing_key)
    if row is None:
        row = {'note_id': existing_key, 'knowledge_id': knowledge_id, 'source_song': song_id,
               'anchor_date': today(), 'step': 0, 'maintenance_step': 0,
               'due_date': (date.today() + timedelta(days=initial[0])).isoformat(),
               'status': 'due_later', 'attempts': []}
    else:
        row['knowledge_id'] = knowledge_id
        row.setdefault('maintenance_step', 0)
        if 'anchor_date' not in row:
            source = row.get('source_song')
            cycle = read_json(base / 'data/songs' / source / 'cycle.json', {}) if source else {}
            row['anchor_date'] = cycle.get('finished_at', today())[:10]
        if row['status'] == 'finished' and (enabled or item['status'] != 'consolidated'):
            row.update(status='needs_reinforcement', step=0, maintenance_step=0,
                       anchor_date=today(), due_date=(date.today()+timedelta(days=1)).isoformat())
    queue[existing_key] = row
    write_json(_path(base), queue)
    return row


def schedule_song(base, song_id):
    for item in mastery.items(base).values():
        if song_id in item['source_songs']:
            schedule(base, item['id'], song_id)


def grade(base, note_id, correct, evidence, *, attempt_id=None,
          assistance=None, context=None, question=None, answer=None):
    initial, maintenance, enabled = _policy(base)
    queue = read_json(_path(base), {})
    row = queue.get(note_id)
    if not row:
        raise ValueError('Nota não encontrada na fila de revisões')
    prior = next((a for a in row['attempts'] if attempt_id and a.get('id') == attempt_id), None)
    if prior:
        if (prior['correct'], prior['evidence'], prior['assistance'], prior['context'],
            prior['question'], prior['answer']) != (correct, evidence, assistance, context, question, answer):
            raise ValueError('ID de revisão já utilizado com outros dados')
        return row
    if row['status'] == 'finished':
        raise ValueError('Revisão concluída; reabra com nova evidência')
    if row['due_date'] > today():
        raise ValueError('Revisão ainda não venceu')
    if assistance not in ('independent', 'assisted') or not all(
            isinstance(s, str) and s.strip() for s in (attempt_id, context, question, answer, evidence)):
        raise ValueError('Informe ID, assistência, contexto, questão, resposta e feedback reais')
    knowledge_id = row.get('knowledge_id') or note_id
    # Mastery write is idempotent by attempt ID; retries cannot duplicate evidence.
    mastered = mastery.record(base, knowledge_id, 'review:'+attempt_id, 'review',
                               'correct' if correct else 'incorrect', assistance,
                               context, question, answer, evidence)
    row['knowledge_id'] = knowledge_id
    row['attempts'].append({'id': attempt_id, 'at': now(), 'correct': correct,
                            'evidence': evidence, 'assistance': assistance, 'context': context,
                            'question': question, 'answer': answer})
    row.setdefault('maintenance_step', 0)
    if 'anchor_date' not in row:
        source = row.get('source_song')
        cycle = read_json(base / 'data/songs' / source / 'cycle.json', {}) if source else {}
        row['anchor_date'] = cycle.get('finished_at', today())[:10]
    anchor = date.fromisoformat(row['anchor_date'])
    current = date.today()
    if not correct or assistance != 'independent':
        if row['step'] >= len(initial):
            row['step'] = 0
            row['anchor_date'] = today()
        row['maintenance_step'] = 0
        row.update(status='needs_reinforcement', due_date=(current+timedelta(days=1)).isoformat())
    else:
        row['step'] += 1
        if row['step'] < len(initial):
            due = max(anchor+timedelta(days=initial[row['step']]), current+timedelta(days=1))
            row.update(status='due_later', due_date=due.isoformat())
        elif mastered['status'] != 'consolidated':
            row.update(status='needs_reinforcement', due_date=(current+timedelta(days=7)).isoformat())
        elif not enabled:
            row['status'] = 'finished'
        else:
            # Maintenance values are successive gaps after the last success.
            index = min(row['maintenance_step'], len(maintenance)-1)
            row.update(status='maintenance', due_date=(current+timedelta(days=maintenance[index])).isoformat(),
                       maintenance_step=min(index+1, len(maintenance)-1))
    queue[note_id] = row
    write_json(_path(base), queue)
    return row
