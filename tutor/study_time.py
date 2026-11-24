"""Confirmed study durations. Chat uptime is not study time."""
from __future__ import annotations
from datetime import date
from pathlib import Path
from uuid import uuid4
from .store import read_json, write_json, read_yaml, now, today, state, require_workspace

ACTIVITIES = ('review', 'music', 'reading', 'writing', 'listening', 'speaking',
              'grammar', 'vocabulary', 'assessment', 'notes', 'other')


def _path(base):
    return base / 'data/study_sessions/sessions.json'


def sessions(base):
    return read_json(_path(base), {})


def _minutes(value, allow_zero=True):
    if type(value) is not int or not (0 if allow_zero else 1) <= value <= 1440:
        raise ValueError('Minutos devem ser inteiros válidos (até 1440)')


def begin(base: Path, planned_minutes: int | None = None, session_id: str | None = None):
    require_workspace(base)
    records = sessions(base)
    if session_id and session_id in records:
        existing = records[session_id]
        if planned_minutes is not None and existing['planned_minutes'] != planned_minutes:
            raise ValueError('Sessão já existe com outro planejamento')
        return existing
    active = next((x for x in records.values() if x['status'] == 'active'), None)
    if active:
        if session_id and session_id != active['id']:
            raise ValueError('Finalize a sessão de estudo ativa antes de iniciar outra')
        return active
    if planned_minutes is None:
        planned_minutes = read_yaml(base / 'config.yaml').get('schedule', {}).get('minutes_per_session')
    if planned_minutes is not None:
        _minutes(planned_minutes, False)
    song_id = state(base).get('active_song')
    cycle = read_json(base / 'data/songs' / song_id / 'cycle.json', {}) if song_id else {}
    identifier = session_id or uuid4().hex
    row = {'id': identifier, 'song_id': song_id, 'study_day': cycle.get('day'),
           'started_at': now(), 'date': today(), 'planned_minutes': planned_minutes,
           'effective_minutes': None, 'measurement_method': None, 'status': 'active',
           'activities': {}}
    records[identifier] = row
    write_json(_path(base), records)
    return row


def record(base, session_id, activity_id, kind, minutes):
    _minutes(minutes)
    if kind not in ACTIVITIES or not activity_id.strip():
        raise ValueError('Tipo de atividade ou ID inválido')
    records = sessions(base)
    row = records.get(session_id)
    if not row:
        raise ValueError('Sessão não encontrada')
    entry = {'id': activity_id, 'type': kind, 'minutes': minutes}
    if activity_id in row['activities']:
        if row['activities'][activity_id] != entry:
            raise ValueError('Atividade já registrada com outros dados')
        return row
    if row['status'] != 'active':
        raise ValueError('Sessão não está ativa')
    row['activities'][activity_id] = entry
    write_json(_path(base), records)
    return row


def finish(base, session_id, effective_minutes=None):
    if effective_minutes is not None:
        _minutes(effective_minutes)
    records = sessions(base)
    row = records.get(session_id)
    if not row:
        raise ValueError('Sessão não encontrada')
    if row['status'] == 'completed':
        if row['effective_minutes'] != effective_minutes:
            raise ValueError('Sessão já concluída com outro valor')
        return row
    allocated = sum(x['minutes'] for x in row['activities'].values())
    if effective_minutes is not None and allocated > effective_minutes:
        raise ValueError('Soma das atividades excede duração confirmada')
    row.update(status='completed', ended_at=now(), effective_minutes=effective_minutes,
               measurement_method='student_confirmed' if effective_minutes is not None else None)
    write_json(_path(base), records)
    return row


def summary(base, start=None, end=None):
    if start:
        date.fromisoformat(start)
    if end:
        date.fromisoformat(end)
    if start and end and start > end:
        raise ValueError('Período invertido')
    rows = [x for x in sessions(base).values() if x['status'] == 'completed'
            and (not start or x['date'] >= start) and (not end or x['date'] <= end)]
    confirmed = [x for x in rows if x['effective_minutes'] is not None]
    comparable = [x for x in confirmed if x['planned_minutes'] is not None]
    planned = sum(x['planned_minutes'] for x in comparable)
    effective = sum(x['effective_minutes'] for x in confirmed)
    by_activity = {}
    for row in confirmed:
        allocated = 0
        for activity in row['activities'].values():
            kind = activity['type']
            by_activity[kind] = by_activity.get(kind, 0) + activity['minutes']
            allocated += activity['minutes']
        by_activity['unallocated'] = by_activity.get('unallocated', 0) + row['effective_minutes'] - allocated
    return {'sessions_completed': len(rows), 'sessions_confirmed': len(confirmed),
            'sessions_unknown_duration': len(rows)-len(confirmed),
            'effective_minutes': effective if confirmed else None,
            'effective_hours': round(effective/60, 3) if confirmed else None,
            'study_days_confirmed': len({x['date'] for x in confirmed if x['effective_minutes'] > 0}),
            'planned_minutes_comparable': planned if comparable else None,
            'adherence': round(sum(x['effective_minutes'] for x in comparable)/planned, 4) if planned else None,
            'by_activity_minutes': by_activity}
