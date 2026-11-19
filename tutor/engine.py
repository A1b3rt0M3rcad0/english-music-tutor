"""Engine local: estado, diagnóstico, sessões, notas e revisões.

Sem avaliação por IA embutida: Codex conduz e fornece EVIDÊNCIA; esta camada
apenas persiste/verifica o que o agente efetivamente demonstrou.
"""
from __future__ import annotations
import hashlib
from datetime import date, timedelta
from pathlib import Path

from .store import (root, now, today, slug, state, save_state, read_json,
                    write_json, read_yaml, write_yaml, write_text, event, require_workspace)

LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'not_assessed')
SKILLS = ('grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking')


def checked_config(base: Path) -> dict:
    require_workspace(base)
    cfg = read_yaml(base / 'config.yaml')
    if cfg.get('schema_version') != 1:
        raise ValueError('config.yaml: schema_version deve ser 1')
    return cfg


def validate_schedule(cfg: dict, complete=False) -> list[str]:
    errors = []
    schedule = cfg.get('schedule') or {}
    for k, lo, hi in [('days_per_week', 1, 7), ('sessions_per_day', 1, 6),
                       ('minutes_per_session', 15, 240)]:
        n = schedule.get(k)
        if n is None and not complete:
            continue
        if not isinstance(n, int) or isinstance(n, bool) or not lo <= n <= hi:
            errors.append(f'schedule.{k}: informe inteiro entre {lo} e {hi}')
    mode = schedule.get('mode')
    if mode not in ('fixed', 'continuous') and (complete or mode is not None):
        errors.append('schedule.mode: fixed ou continuous')
    if mode == 'fixed':
        n = schedule.get('duration_days')
        if not isinstance(n, int) or n < 1 or n > 36500:
            errors.append('schedule.duration_days: inteiro positivo (máximo 36500)')
    elif mode == 'continuous' and schedule.get('duration_days') is not None:
        errors.append('schedule.duration_days: null para duração contínua')
    if complete and not (cfg.get('student') or {}).get('learning_goal'):
        errors.append('student.learning_goal: obrigatório')
    return errors


def update_profile(base: Path, data: dict) -> dict:
    cfg = checked_config(base)
    cfg.setdefault('student', {}).update(data['student'])
    cfg.setdefault('schedule', {}).update(data['schedule'])
    cfg.setdefault('method', {})['voice_mode'] = data['voice_mode']
    errs = validate_schedule(cfg, complete=True)
    if errs:
        raise ValueError('; '.join(errs))
    write_yaml(base / 'config.yaml', cfg)
    s = state(base)
    s['onboarded'] = True
    save_state(base, s)
    event(base, 'onboarded', {'goal': cfg['student']['learning_goal']})
    return cfg


def record_diagnostic(base: Path, skill: str, difficulty: str, question: str,
                      answer: str, score: float, feedback: str, evidence_mode: str) -> dict:
    if skill not in SKILLS:
        raise ValueError('skill inválida: ' + ', '.join(SKILLS))
    if not (0 <= score <= 1):
        raise ValueError('score deve estar entre 0 e 1')
    if difficulty not in LEVELS[:-1]:
        raise ValueError('difficulty deve ser A1..C2')
    if evidence_mode not in ('text', 'audio', 'external_verified'):
        raise ValueError('evidence_mode: text | audio | external_verified')
    if not question.strip() or not answer.strip() or not feedback.strip():
        raise ValueError('Pergunta, resposta e feedback são obrigatórios')
    basepath = base / 'data/assessments/placement/items.json'
    items = read_json(basepath, [])
    item = {'id': len(items)+1, 'at': now(), 'skill': skill,
            'difficulty': difficulty, 'question': question,
            'answer': answer, 'score': round(score, 3),
            'feedback': feedback, 'evidence_mode': evidence_mode}
    items.append(item)
    write_json(basepath, items)
    event(base, 'diagnostic_item', {'id': item['id'], 'skill': skill, 'score': score})
    return item


def finish_diagnostic(base: Path, levels: dict, summary: str) -> dict:
    s = state(base)
    if not s.get('onboarded'):
        raise ValueError('Faça onboarding primeiro')
    items = read_json(base / 'data/assessments/placement/items.json', [])
    if len(items) < 10:
        raise ValueError(f'Diagnóstico incompleto: {len(items)} respostas; mínimo 10')
    if not summary.strip():
        raise ValueError('Informe justificativa da avaliação')
    for name in SKILLS:
        level = levels.get(name, 'not_assessed')
        if level not in LEVELS:
            raise ValueError(f'Nível inválido em {name}: {level}')
        if level != 'not_assessed' and not any(x['skill'] == name for x in items):
            raise ValueError(f'{name} foi nivelado sem qualquer evidência')
        if name == 'speaking' and level != 'not_assessed' and not any(
            x['skill'] == 'speaking' and x['evidence_mode'] in ('audio', 'external_verified')
            for x in items
        ):
            # texto permite avaliação de produção interativa, mas não de pronúncia.
            # Marcar nível como provisório, sem fabricar avaliação acústica.
            pass
    report = {'at': now(), 'levels': levels, 'summary': summary,
              'evidence_count': len(items), 'limitations': []}
    for skill in SKILLS:
        if levels.get(skill, 'not_assessed') == 'not_assessed':
            report['limitations'].append(f'{skill}: não avaliado')
    if levels.get('speaking') != 'not_assessed' and not any(
        x['skill'] == 'speaking' and x['evidence_mode'] in ('audio', 'external_verified')
        for x in items):
        report['limitations'].append('speaking: estimativa de produção textual; pronúncia não verificada')
    write_yaml(base / 'data/assessments/placement/report.yaml', report)
    cfg = checked_config(base)
    cfg['assessment']['placement_status'] = 'completed'
    cfg['assessment']['diagnostic_date'] = today()
    write_yaml(base / 'config.yaml', cfg)
    s['diagnostic_done'] = True
    save_state(base, s)
    event(base, 'diagnostic_finished', {'levels': levels})
    return report


def create_roadmap(base: Path) -> dict:
    cfg = checked_config(base)
    if not state(base)['diagnostic_done']:
        raise ValueError('Finalize o diagnóstico antes do roadmap')
    sch = cfg['schedule']
    if sch['mode'] == 'continuous':
        horizon = cfg['roadmap'].get('planning_horizon_days', 90)
    else:
        horizon = sch['duration_days']
    study_days = horizon * sch['days_per_week'] / 7
    estimated = int(study_days // cfg['method']['default_study_days_per_song'])
    levels = read_yaml(base / 'data/assessments/placement/report.yaml')['levels']
    hours = study_days * sch['sessions_per_day'] * sch['minutes_per_session']/60
    previous = read_yaml(base / 'data/roadmap.yaml') if (base / 'data/roadmap.yaml').exists() else None
    history = (previous.get('history', []) + [{k: v for k, v in previous.items() if k != 'history'}]) if previous else []
    result = {
        'generated_at': now(), 'mode': sch['mode'], 'horizon_days': horizon,
        'goal': cfg['student']['learning_goal'], 'target_cefr': cfg['student'].get('target_cefr'),
        'initial_levels': levels,
        'available_hours_estimate': round(hours, 1),
        'nominal_song_capacity': estimated,
        'estimate_note': 'Capacidade nominal antes de feriados, faltas e testes extras. Não garante CEFR.',
        'phases': [
            {'id': 1, 'name': 'Consolidação', 'focus': 'Lacunas evidenciadas no diagnóstico',
             'criteria': 'Evidências em exercícios inéditos, listening e produção'},
            {'id': 2, 'name': 'Transferência', 'focus': 'Chunks ativos, conversação e compreensão sem letra',
             'criteria': 'Utilização sem consulta em contextos diferentes'},
            {'id': 3, 'name': 'Autonomia', 'focus': 'Complexidade crescente e reavaliação',
             'criteria': 'Teste independente + justificativa por competência'}
        ], 'history': history
    }
    write_yaml(base / 'data/roadmap.yaml', result)
    cfg['roadmap']['status'] = 'active'
    write_yaml(base / 'config.yaml', cfg)
    s = state(base); s['roadmap_ready'] = True; save_state(base, s)
    event(base, 'roadmap_created', {'nominal_song_capacity': estimated})
    return result


def active_song(base: Path) -> tuple[dict, Path]:
    s = state(base)
    name = s.get('active_song')
    if not name:
        raise ValueError('Nenhuma música ativa. Execute song start.')
    path = base / 'data/songs' / name
    return read_json(path / 'cycle.json'), path


def start_song(base: Path, title: str, artist: str, source: str) -> dict:
    s = state(base)
    if not s.get('roadmap_ready'):
        raise ValueError('Faça onboarding, diagnóstico e roadmap antes da música')
    if s.get('active_song'):
        raise ValueError('Finalize a música atual antes de iniciar outra')
    index = s.get('songs_completed', 0) + 1
    identifier = f'{index:03d}-{slug(title)}'
    path = base / 'data/songs' / identifier
    if path.exists():
        raise ValueError(f'Pasta de música já existe: {identifier}')
    ctx = read_json(base / '.tutor/session.json', {})
    thread_id = ctx.get('session_id')
    known_threads_path = base / 'data/threads.json'
    known_threads = read_json(known_threads_path, {})
    if thread_id and thread_id in known_threads:
        raise ValueError('Este chat já foi utilizado para outra música; abra um novo chat para cada música.')
    record = {'id': identifier, 'title': title, 'artist': artist,
              'source': source, 'started_at': now(), 'started_on': today(),
              'thread_id': thread_id, 'day': 1, 'status': 'active',
              'days': {'1': {'status': 'pending', 'activities': []},
                       '2': {'status': 'pending', 'activities': []},
                       '3': {'status': 'pending', 'activities': []}}}
    write_json(path / 'cycle.json', record)
    write_text(path / 'README.md', f'# {title} — {artist}\n\nMúsica: {identifier}\n\n'
               f'Origem: {source or "informada pelo aluno"}\n\n'
               'Anotações: links nas notas em `../../notes/` e avaliações no `cycle.json`.\n'
               'Não salvar letra integral sem direitos de reprodução.\n')
    if thread_id:
        known_threads[thread_id] = identifier
        write_json(known_threads_path, known_threads)
    s['active_song'] = identifier
    save_state(base, s)
    event(base, 'song_started', {'id': identifier, 'title': title})
    return record


def check_thread(base: Path, record: dict) -> None:
    current = read_json(base / '.tutor/session.json', {}).get('session_id')
    bound = record.get('thread_id')
    if bound and current and bound != current:
        raise ValueError('Esta música pertence a outro chat. Retome o chat original para continuar os dias 1–3.')


def begin_day(base: Path, day: int) -> dict:
    record, path = active_song(base)
    check_thread(base, record)
    if day != record['day']:
        raise ValueError(f'Dia esperado: {record["day"]}; solicitado: {day}')
    d = record['days'][str(day)]
    if d['status'] == 'completed':
        raise ValueError('Dia já concluído')
    d['status'] = 'in_progress'
    d.setdefault('started_at', now())
    write_json(path / 'cycle.json', record)
    event(base, 'day_started', {'song': record['id'], 'day': day})
    return record


def checkpoint(base: Path, day: int, activity: str, evidence: str,
               feedback: str, score: float | None) -> dict:
    record, path = active_song(base)
    check_thread(base, record)
    if record['day'] != day or record['days'][str(day)]['status'] != 'in_progress':
        raise ValueError('Inicie o dia correto antes de registrar atividade')
    if not activity.strip() or not evidence.strip() or not feedback.strip():
        raise ValueError('Atividade, evidência e feedback são obrigatórios; não invente respostas')
    if score is not None and not 0 <= score <= 1:
        raise ValueError('score de 0 a 1')
    entry = {'at': now(), 'activity': activity, 'evidence': evidence,
             'feedback': feedback, 'score': score}
    record['days'][str(day)]['activities'].append(entry)
    write_json(path / 'cycle.json', record)
    event(base, 'checkpoint', {'song': record['id'], 'day': day, 'activity': activity})
    return entry


def end_day(base: Path, day: int, summary: str) -> dict:
    record, path = active_song(base)
    check_thread(base, record)
    if day != record['day'] or record['days'][str(day)]['status'] != 'in_progress':
        raise ValueError('Dia errado ou ainda não iniciado')
    if not record['days'][str(day)]['activities']:
        raise ValueError('Registre pelo menos uma atividade com evidência antes de encerrar')
    if not summary.strip():
        raise ValueError('É obrigatório resumir o desempenho')
    dayrec = record['days'][str(day)]
    dayrec.update({'status': 'completed', 'ended_at': now(), 'summary': summary})
    write_text(path / f'day-{day}.md', f'# Dia {day} — {record["title"]}\n\n'
               f'Data: {today()}\n\nResumo: {summary}\n\n' + '\n'.join(
               f'- {e["activity"]}: {e["feedback"]} (evidência: {e["evidence"]})'
               for e in dayrec['activities']) + '\n')
    if day < 3:
        record['day'] = day+1
    write_json(path / 'cycle.json', record)
    event(base, 'day_finished', {'song': record['id'], 'day': day})
    return record


def add_note(base: Path, kind: str, title: str, meaning: str,
             example: str, evidence: str, tags: list[str]) -> dict:
    folder = {'expression':'expressions', 'grammar':'grammar',
              'pronunciation':'pronunciation', 'difficulty':'difficulties'}.get(kind)
    if not folder:
        raise ValueError('type: expression | grammar | pronunciation | difficulty')
    if not all(x.strip() for x in (title, meaning, example, evidence)):
        raise ValueError('Título, significado, exemplo e evidência são obrigatórios')
    active = state(base).get('active_song')
    if not active:
        raise ValueError('Notas de música exigem música ativa')
    identifier = slug(title)
    dest = base / 'data/notes' / folder / (identifier + '.md')
    song_rel = f'../../songs/{active}/README.md'
    # slug e título são originados de dados externos e nunca usados como código.
    source_link = f'[Música {active}]({song_rel})'
    if not dest.exists():
        header = f'# {title}\n\nTipo: {kind}\nSignificado: {meaning}\n'
        if tags:
            header += 'Tags: ' + ', '.join(tags) + '\n'
        header += '\n## Histórico de evidências\n'
    else:
        header = dest.read_text(encoding='utf-8')
    header += (f'\n### {today()} — {source_link}\n'
               f'- Exemplo do aluno: {example}\n- Evidência/avaliação: {evidence}\n')
    write_text(dest, header)
    notes_index = base / 'data/notes/index.json'
    idx = read_json(notes_index, {})
    note_id = f'{folder}/{identifier}'
    idx[note_id] = {'id': note_id, 'title': title, 'type': kind,
                    'file': str(dest.relative_to(base)), 'latest_song': active,
                    'updated_at': now()}
    write_json(notes_index, idx)
    event(base, 'note_updated', {'note': note_id, 'song': active})
    return idx[note_id]


def finish_song(base: Path, comprehension: int, expressions: int,
                pronunciation: str, speaking: str, summary: str) -> dict:
    record, path = active_song(base)
    check_thread(base, record)
    if any(x['status'] != 'completed' for x in record['days'].values()):
        raise ValueError('Os três dias precisam estar concluídos antes da avaliação final')
    if not 0 <= comprehension <= 100 or not 0 <= expressions <= 8:
        raise ValueError('Compreensão deve estar em 0..100 e expressões em 0..8')
    if pronunciation not in ('verified', 'needs_work', 'not_assessed'):
        raise ValueError('pronunciation: verified | needs_work | not_assessed')
    if not speaking.strip() or not summary.strip():
        raise ValueError('Speaking e avaliação textual são obrigatórios; use not_assessed se necessário')
    final = {'at': now(), 'comprehension_percent': comprehension,
             'active_expressions': expressions, 'pronunciation_status': pronunciation,
             'speaking_evidence': speaking, 'summary': summary,
             'criteria': {'comprehension': comprehension>=80,
                          'expressions': expressions>=5,
                          'pronunciation': pronunciation=='verified',
                          'speaking': speaking != 'not_assessed'}}
    record['status'] = 'completed'
    record['finished_at'] = now()
    record['final'] = final
    write_json(path / 'cycle.json', record)
    write_yaml(path / 'assessment.yaml', final)
    cfg = checked_config(base)
    reviews_file = base / 'data/reviews.json'
    reviews = read_json(reviews_file, {})
    index = read_json(base / 'data/notes/index.json', {})
    intervals = cfg['method']['review_intervals_days']
    finished = date.today()
    for note_id, note in index.items():
        if note['latest_song'] == record['id'] and note['type'] == 'expression':
            # preserve already scheduled revisions for a known expression
            if note_id not in reviews:
                reviews[note_id] = {'note_id': note_id, 'source_song': record['id'],
                                    'step': 0, 'due_date': (finished + timedelta(days=intervals[0])).isoformat(),
                                    'status': 'due_later', 'attempts': []}
    write_json(reviews_file, reviews)
    s = state(base)
    s['songs_completed'] = s.get('songs_completed', 0) + 1
    s['active_song'] = None
    save_state(base, s)
    event(base, 'song_finished', {'song': record['id'], 'criteria': final['criteria']})
    return final


def due_reviews(base: Path, day: str | None = None) -> list[dict]:
    date_str = day or today()
    return [r for r in read_json(base / 'data/reviews.json', {}).values()
            if r['status'] != 'finished' and r['due_date'] <= date_str]


def grade_review(base: Path, note_id: str, correct: bool, evidence: str) -> dict:
    if not evidence.strip():
        raise ValueError('Informe a resposta do aluno ou evidência observada')
    cfg = checked_config(base)
    reviews_file = base / 'data/reviews.json'
    reviews = read_json(reviews_file, {})
    if note_id not in reviews:
        raise ValueError('Nota não encontrada na fila de revisões')
    item = reviews[note_id]
    if item['status'] == 'finished':
        raise ValueError('Revisão concluída definitivamente')
    if item['due_date'] > today():
        raise ValueError('Revisão ainda não venceu')
    item['attempts'].append({'at': now(), 'correct': correct, 'evidence': evidence})
    if correct:
        item['step'] += 1
        intervals = cfg['method']['review_intervals_days']
        if item['step'] >= len(intervals):
            item['status'] = 'finished'
        else:
            # D+3, D+7 etc. a partir da data de encerramento da música.
            # Atrasos mantêm progressão sem retroagir datas no calendário.
            song = read_json(base / 'data/songs' / item['source_song'] / 'cycle.json')
            ended = date.fromisoformat(song['finished_at'][:10])
            scheduled = ended + timedelta(days=intervals[item['step']])
            item['due_date'] = max(scheduled, date.today() + timedelta(days=1)).isoformat()
            item['status'] = 'due_later'
    else:
        item['due_date'] = (date.today() + timedelta(days=1)).isoformat()
        item['status'] = 'needs_reinforcement'
    write_json(reviews_file, reviews)
    event(base, 'review_graded', {'note': note_id, 'correct': correct})
    return item


def metrics(base: Path) -> dict:
    s = state(base)
    reviews = read_json(base / 'data/reviews.json', {})
    cfg = checked_config(base)
    return {'onboarded': s.get('onboarded', False),
            'diagnostic_done': s.get('diagnostic_done', False),
            'roadmap_ready': s.get('roadmap_ready', False),
            'active_song': s.get('active_song'),
            'songs_completed': s.get('songs_completed', 0),
            'reviews_due': len(due_reviews(base)),
            'notes_total': len(read_json(base / 'data/notes/index.json', {})),
            'mode': cfg['schedule']['mode']}
