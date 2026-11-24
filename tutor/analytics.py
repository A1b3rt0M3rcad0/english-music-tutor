"""Derived metrics; missing evidence is unknown, not a zero score."""
from __future__ import annotations
from collections import Counter
from datetime import date, timedelta
from .store import read_json, today
from . import mastery, cefr, study_time


def rate(n, d):
    return {'value': round(n/d, 4) if d else None, 'numerator': n, 'sample_size': d}


def cycles(base):
    return [read_json(p) for p in sorted((base / 'data/songs').glob('*/cycle.json'))]


def summary(base, start=None, end=None):
    time = study_time.summary(base, start, end)
    def within(timestamp):
        day = timestamp[:10]
        return (not start or day >= start) and (not end or day <= end)
    completed = [x for x in cycles(base) if x['status'] == 'completed'
                 and within(x['finished_at'])]
    knowledge = list(mastery.items(base).values())
    attempts = [a for x in knowledge for a in x['attempts'] if within(a['at'])]
    transfer = [a for a in attempts if a['mode'] == 'transfer' and
                a['assistance'] == 'independent' and a['outcome'] in ('correct', 'incorrect', 'not_observed')]
    reviews = [a for a in attempts if a['mode'] == 'review' and
               a['assistance'] == 'independent' and a['outcome'] in ('correct', 'incorrect')]
    # Counts of current mastery are a snapshot, even for period reports.
    counts = mastery.summary(base)
    comprehension = [x['final']['comprehension_percent'] for x in completed
                     if x.get('final', {}).get('comprehension_percent') is not None]
    # Existing comprehension values are agent estimates, not a pooled item accuracy.
    review_queue = read_json(base / 'data/reviews.json', {})
    grouped = {}
    for cycle in cycles(base):
        for day in cycle.get('days', {}).values():
            for a in day['activities']:
                if a.get('skill') and a.get('difficulty') and a.get('score') is not None and within(a['at']):
                    grouped.setdefault((a['skill'], a['difficulty']), []).append(a['score'])
    breakdown = [{'skill': skill, 'difficulty': difficulty, 'mean_score': round(sum(scores)/len(scores),4),
                  'sample_size': len(scores)} for (skill,difficulty),scores in sorted(grouped.items())]
    return {'period': {'start': start, 'end': end}, 'study': time,
            'cefr_current': cefr.current(base), 'cefr_due': cefr.due(base),
            'songs_completed': len(completed), 'knowledge_current': counts,
            'acquisition_current': rate(counts['acquired_total'], counts['total']),
            'consolidation_current': rate(counts['by_status']['consolidated'], counts['total']),
            'transfer': rate(sum(a['outcome'] == 'correct' for a in transfer), len(transfer)),
            'retention': rate(sum(a['outcome'] == 'correct' for a in reviews), len(reviews)),
            'comprehension_mean': {'value': round(sum(comprehension)/len(comprehension), 2) if comprehension else None,
                                   'sample_size': len(comprehension), 'unit': 'percent',
                                   'method': 'unweighted_song_estimates'},
            'reviews_due_current': sum(r['status'] != 'finished' and r['due_date'] <= today()
                                       for r in review_queue.values()),
            'performance_by_skill_difficulty': breakdown,
            'difficulties': difficulties(base, start, end)}


def difficulties(base, start=None, end=None):
    rows = []
    for item in mastery.items(base).values():
        failures = [a for a in item['attempts'] if a['outcome'] == 'incorrect'
                    and (not start or a['at'][:10] >= start)
                    and (not end or a['at'][:10] <= end)]
        if failures:
            rows.append({'knowledge_id': item['id'], 'content': item['content'],
                         'type': item['type'], 'failures': len(failures), 'status': item['status']})
    tags = Counter()
    for cycle in cycles(base):
        for day in cycle.get('days', {}).values():
            for activity in day['activities']:
                if activity.get('error_tag') and (not start or activity['at'][:10] >= start) and (not end or activity['at'][:10] <= end):
                    tags[activity['error_tag']] += 1
    return {'knowledge': sorted(rows, key=lambda x: (-x['failures'], x['knowledge_id'])),
            'error_tags': dict(tags.most_common())}


def trends(base):
    return [{'song_id': x['id'], 'finished_at': x['finished_at'],
             'comprehension_percent': x.get('final', {}).get('comprehension_percent'),
             'difficulty': x.get('difficulty'),
             'independent_transfer': rate(
                 sum(a['outcome'] == 'correct' for item in mastery.items(base).values()
                     for a in item['attempts'] if a.get('song_id') == x['id'] and a['mode'] == 'transfer'
                     and a['assistance'] == 'independent'),
                 sum(a['outcome'] in ('correct', 'incorrect', 'not_observed') for item in mastery.items(base).values()
                     for a in item['attempts'] if a.get('song_id') == x['id'] and a['mode'] == 'transfer'
                     and a['assistance'] == 'independent'))}
            for x in cycles(base) if x['status'] == 'completed']


def period(base, name):
    end = date.today()
    start = end - timedelta(days=end.weekday()) if name == 'weekly' else end.replace(day=1)
    return summary(base, start.isoformat(), end.isoformat())
