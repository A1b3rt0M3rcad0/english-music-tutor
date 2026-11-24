"""Longitudinal, provisional CEFR estimates by dimension, not certification."""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from .store import read_json, write_json, read_yaml, now, state, require_workspace
from . import study_time

LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'not_assessed')
SKILLS = ('grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking')
EVIDENCE = ('text', 'audio', 'external_verified')


def _path(base):
    return base / 'data/assessments/cefr/assessments.json'


def records(base):
    return read_json(_path(base), {})


def _snapshot(base):
    p = base / 'data/assessments/placement/report.yaml'
    if not p.is_file():
        return None
    report = read_yaml(p)
    source = read_json(base / 'data/assessments/placement/items.json', [])
    levels = dict(report['levels'])
    for skill in ('listening', 'speaking'):
        if not any(x['skill'] == skill and x['evidence_mode'] in ('audio', 'external_verified') for x in source):
            levels[skill] = 'not_assessed'
    return {'id': 'placement', 'type': 'placement', 'status': 'completed',
            'at': report['at'], 'levels': {k: levels.get(k, 'not_assessed') for k in SKILLS},
            'items': source, 'summary': report['summary'],
            'limitations': list(report.get('limitations', [])) + ['Estimativa inicial legada; não certificação.'],
            'songs_completed': 0, 'effective_minutes': 0}


def preserve_placement(base):
    all_records = records(base)
    if 'placement' not in all_records:
        initial = _snapshot(base)
        if initial:
            all_records['placement'] = initial
            write_json(_path(base), all_records)
    return all_records.get('placement')


def history(base):
    all_records = records(base)
    if 'placement' not in all_records:
        initial = _snapshot(base)
        if initial:
            all_records['placement'] = initial
    return sorted((x for x in all_records.values() if x['status'] == 'completed'),
                  key=lambda x: (x['type'] != 'placement', x['at']))


def current(base):
    entries = history(base)
    levels = {}
    for row in entries:
        for skill, level in row['levels'].items():
            if level != 'not_assessed':
                levels[skill] = {'level': level, 'assessment_id': row['id'], 'assessed_at': row['at']}
    return {'levels': {k: levels.get(k, {'level': 'not_assessed', 'assessment_id': None, 'assessed_at': None})
                       for k in SKILLS},
            'latest_assessment': entries[-1]['id'] if entries else None,
            'latest_assessment_levels': entries[-1]['levels'] if entries else None,
            'target_cefr': read_yaml(base / 'config.yaml').get('student', {}).get('target_cefr'),
            'global_cefr': None, 'status': 'provisional' if entries else 'not_assessed'}


def due(base):
    cfg = read_yaml(base / 'config.yaml').get('cefr_progression', {})
    song_interval = cfg.get('songs_interval', 5)
    minute_interval = cfg.get('minutes_interval', 1800)
    if any(type(n) is not int or n <= 0 for n in (song_interval, minute_interval)):
        raise ValueError('Intervalos CEFR devem ser inteiros positivos')
    entries = history(base)
    if not entries:
        return {'due': False, 'reason': 'placement_required'}
    last = entries[-1]
    songs = max(0, state(base).get('songs_completed', 0) - last['songs_completed'])
    minutes = max(0, (study_time.summary(base)['effective_minutes'] or 0) - last['effective_minutes'])
    active = next((x['id'] for x in records(base).values() if x['status'] == 'active'), None)
    return {'due': bool(active or songs >= song_interval or minutes >= minute_interval),
            'active_assessment': active, 'songs_since': songs, 'minutes_since': minutes,
            'songs_threshold': song_interval, 'minutes_threshold': minute_interval}


def begin(base: Path):
    require_workspace(base)
    if not state(base).get('diagnostic_done'):
        raise ValueError('Finalize o diagnóstico inicial')
    preserve_placement(base)
    all_records = records(base)
    active = next((x for x in all_records.values() if x['status'] == 'active'), None)
    if active:
        return active
    identifier = uuid4().hex
    row = {'id': identifier, 'type': 'progression', 'status': 'active',
           'started_at': now(), 'items': []}
    all_records[identifier] = row
    write_json(_path(base), all_records)
    return row


def record(base, assessment_id, item_id, skill, difficulty, question, answer, score,
           feedback, evidence_mode='text'):
    all_records = records(base)
    row = all_records.get(assessment_id)
    if not row or row['status'] != 'active':
        raise ValueError('Avaliação não está ativa')
    if (skill not in SKILLS or difficulty not in LEVELS[:-1] or evidence_mode not in EVIDENCE
            or not all(x.strip() for x in (item_id, question, answer, feedback))
            or isinstance(score, bool) or not 0 <= score <= 1):
        raise ValueError('Dados de avaliação inválidos')
    if skill in ('speaking', 'listening') and evidence_mode == 'text':
        raise ValueError('Competência oral/auditiva exige evidência adequada')
    entry = {'id': item_id, 'skill': skill, 'difficulty': difficulty, 'question': question,
             'answer': answer, 'score': score, 'feedback': feedback, 'evidence_mode': evidence_mode}
    for old in row['items']:
        if old['id'] == item_id:
            if any(old.get(k) != v for k, v in entry.items()):
                raise ValueError('ID já utilizado com outros dados')
            return old
    previous_items = [x for old in history(base) for x in old.get('items', [])]
    if any(x.get('question', '').casefold().strip() == question.casefold().strip()
           for x in row['items'] + previous_items):
        raise ValueError('Utilize uma pergunta inédita')
    entry['at'] = now()
    row['items'].append(entry)
    write_json(_path(base), all_records)
    return entry


def finish(base, assessment_id, levels, summary):
    all_records = records(base)
    row = all_records.get(assessment_id)
    if not row or row['status'] != 'active':
        raise ValueError('Avaliação não está ativa')
    if len(row['items']) < 10 or not summary.strip():
        raise ValueError('Mínimo de 10 itens com evidência e justificativa')
    if set(levels) != set(SKILLS):
        raise ValueError('Informe todas as dimensões, inclusive not_assessed')
    for skill, level in levels.items():
        if level not in LEVELS:
            raise ValueError('Nível inválido')
        if level == 'not_assessed':
            continue
        subset = [x for x in row['items'] if x['skill'] == skill]
        # Operational guardrail, not a psychometrically calibrated CEFR threshold.
        passed = [x for x in subset if LEVELS.index(x['difficulty']) >= LEVELS.index(level)
                  and x['score'] >= .75]
        if len(subset) < 3 or len(passed) < 2:
            raise ValueError(f'{skill}: mínimo de 3 itens e 2 acertos no nível declarado ou superior')
    row.update(status='completed', at=now(), levels=levels, summary=summary,
               limitations=['Estimativa pedagógica provisória; não é certificação CEFR.'] +
                           [f'{k}: não avaliado nesta avaliação' for k, v in levels.items() if v == 'not_assessed'],
               songs_completed=state(base).get('songs_completed', 0),
               effective_minutes=study_time.summary(base)['effective_minutes'] or 0)
    write_json(_path(base), all_records)
    return row
