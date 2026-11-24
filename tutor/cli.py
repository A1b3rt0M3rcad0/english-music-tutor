"""CLI determinística utilizada pelo Codex e pelo aluno."""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .store import root, state, read_json, read_yaml, require_workspace, write_yaml, today
from . import engine as e
from . import mastery, cefr, study_time, analytics, migrations, review_policy



def show(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def ask(label: str, default: str = '') -> str:
    txt = input(f'{label}' + (f' [{default}]' if default else '') + ': ').strip()
    return txt or default


def positive_int(label: str, minimum: int, maximum: int, default: int) -> int:
    while True:
        try:
            n = int(ask(label, str(default)))
            if minimum <= n <= maximum:
                return n
        except ValueError:
            pass
        print(f'Informe um inteiro de {minimum} a {maximum}.')


def onboard(base: Path) -> None:
    print('=== Onboarding do aluno (configuração; nivelamento será feito pelo Codex) ===')
    name = ask('Nome ou apelido (opcional)') or None
    goal = ask('Qual seu objetivo específico com inglês?')
    if not goal:
        raise ValueError('Objetivo é obrigatório')
    target = ask('CEFR desejado (A1/A2/B1/B2/C1/C2 ou vazio)').upper() or None
    if target not in (None, *e.LEVELS[:-1]):
        raise ValueError('CEFR inválido')
    mode = ask('Prazo: fixed (dias) ou continuous (para a vida)', 'fixed').lower()
    if mode not in ('fixed', 'continuous'):
        raise ValueError('mode deve ser fixed ou continuous')
    duration = positive_int('Quantos dias no total?', 1, 36500, 90) if mode == 'fixed' else None
    days = positive_int('Quantos dias por semana?', 1, 7, 7)
    sessions = positive_int('Quantas sessões por dia?', 1, 6, 1)
    minutes = positive_int('Quantos minutos POR SESSÃO?', 15, 240, 120)
    voice = ask('Áudio: external / audio_available / text_only', 'external')
    if voice not in ('external', 'audio_available', 'text_only'):
        raise ValueError('Opção de áudio inválida')
    data = {'student': {'name': name, 'learning_goal': goal, 'target_cefr': target},
            'schedule': {'mode': mode, 'duration_days': duration, 'days_per_week': days,
                         'sessions_per_day': sessions, 'minutes_per_session': minutes},
            'voice_mode': voice}
    show(e.update_profile(base, data))
    print('Configuração salva. Próximo passo: diagnóstico interativo no Codex.')


def doctor(base: Path) -> dict:
    issues = []
    if not (base / 'config.yaml').exists():
        issues.append('Não existe config.yaml. Execute python bootstrap.py workspace na raiz do projeto.')
    else:
        try:
            cfg = e.checked_config(base)
            issues += e.validate_schedule(cfg, complete=state(base).get('onboarded', False))
        except Exception as exc:
            issues.append(str(exc))
    project = Path(__file__).resolve().parent.parent
    for p in ('AGENTS.md', '.agents/skills/music-study-coach/SKILL.md',
              '.codex/hooks.json', 'tutor/hooks.py'):
        if not (project / p).is_file():
            issues.append(f'Arquivo ausente: {p}')
    try:
        import yaml
    except ImportError:
        issues.append('PyYAML não instalado: python -m pip install -e .')
    if not shutil.which('codex'):
        issues.append('Codex CLI ausente no PATH (necessário para a experiência via terminal).')
    return {'workspace': str(base), 'python': sys.version.split()[0],
            'graphify_cli': bool(shutil.which('graphify')),
            'codex_cli': bool(shutil.which('codex')),
            'status': 'ok' if not issues else 'needs_attention', 'issues': issues}


def graph_sync(base: Path, source: str | None) -> dict:
    cfg = e.checked_config(base)
    graphify = shutil.which('graphify')
    if not graphify:
        return {'status': 'not_available', 'detail': 'Instale graphifyy; notas continuam acessíveis em Markdown.'}
    relative = source or cfg['knowledge']['graphify_source']
    target = (base / relative).resolve()
    if target != base and base not in target.parents:
        raise ValueError('Caminho de indexação precisa permanecer no workspace')
    if not target.is_dir():
        raise ValueError(f'Diretório não encontrado: {target}')
    # Chamada deliberadamente síncrona/explicita. Graphify pode fazer chamadas ao backend configurado.
    result = subprocess.run([graphify, str(target)], cwd=base, capture_output=True,
                            text=True, timeout=300, check=False)
    return {'status': 'ok' if result.returncode == 0 else 'failed',
            'returncode': result.returncode,
            'stdout': result.stdout[-3000:], 'stderr': result.stderr[-3000:]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog='python -m tutor.cli', description='Tutor de inglês por músicas')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('status', 'doctor', 'onboard'):
        sub.add_parser(name)
    diag = sub.add_parser('diagnostic'); ds = diag.add_subparsers(dest='action', required=True)
    d = ds.add_parser('record')
    d.add_argument('--skill', required=True, choices=e.SKILLS)
    d.add_argument('--difficulty', required=True, choices=e.LEVELS[:-1])
    d.add_argument('--question', required=True); d.add_argument('--answer', required=True)
    d.add_argument('--score', type=float, required=True)
    d.add_argument('--feedback', required=True)
    d.add_argument('--evidence-mode', default='text', choices=['text','audio','external_verified'])
    f = ds.add_parser('finish')
    for skill in e.SKILLS:
        f.add_argument('--' + skill, required=True, choices=e.LEVELS)
    f.add_argument('--summary', required=True)
    plan = sub.add_parser('roadmap'); plan.add_argument('action', choices=['create','show']); plan.add_argument('--reason', default='')
    song = sub.add_parser('song'); ss = song.add_subparsers(dest='action', required=True)
    s = ss.add_parser('start'); s.add_argument('--title', required=True); s.add_argument('--artist', required=True)
    s.add_argument('--source', default='')
    s = ss.add_parser('begin-day'); s.add_argument('--day', required=True, type=int, choices=[1,2,3])
    s = ss.add_parser('checkpoint'); s.add_argument('--day', required=True, type=int, choices=[1,2,3])
    s.add_argument('--activity', required=True); s.add_argument('--evidence', required=True)
    s.add_argument('--feedback', required=True); s.add_argument('--score', type=float)
    s.add_argument('--skill', choices=e.SKILLS); s.add_argument('--difficulty', choices=e.LEVELS[:-1]); s.add_argument('--error-tag')
    s = ss.add_parser('end-day'); s.add_argument('--day', required=True, type=int, choices=[1,2,3]); s.add_argument('--summary', required=True)
    s = ss.add_parser('finish'); s.add_argument('--comprehension', required=True, type=int)
    s.add_argument('--expressions', required=True, type=int)
    s.add_argument('--pronunciation', required=True, choices=['verified','needs_work','not_assessed'])
    s.add_argument('--speaking', required=True); s.add_argument('--summary', required=True)
    ss.add_parser('current')
    s = ss.add_parser('difficulty'); s.add_argument('--level', required=True, choices=e.LEVELS[:-1]); s.add_argument('--evidence', required=True)
    note = sub.add_parser('note'); ns = note.add_subparsers(dest='action', required=True)
    n = ns.add_parser('add'); n.add_argument('--type', required=True, choices=['expression','grammar','pronunciation','difficulty'])
    n.add_argument('--title', required=True); n.add_argument('--meaning', required=True)
    n.add_argument('--example', required=True); n.add_argument('--evidence', required=True)
    n.add_argument('--tags', default='')
    r = sub.add_parser('review'); rs = r.add_subparsers(dest='action', required=True)
    d = rs.add_parser('due'); d.add_argument('--date')
    g = rs.add_parser('grade'); g.add_argument('--note-id', required=True)
    g.add_argument('--result', required=True, choices=['correct','incorrect'])
    g.add_argument('--evidence', required=True)
    g.add_argument('--attempt-id'); g.add_argument('--assistance', choices=['independent','assisted']); g.add_argument('--context'); g.add_argument('--question'); g.add_argument('--answer')
    graph = sub.add_parser('graph'); gs = graph.add_subparsers(dest='action', required=True)
    g = gs.add_parser('sync'); g.add_argument('--source')
    sub.add_parser('migrate')
    k = sub.add_parser('knowledge').add_subparsers(dest='action', required=True)
    for action in ('list', 'summary', 'gaps'):
        k.add_parser(action)
    s = k.add_parser('show'); s.add_argument('--id', required=True)
    s = k.add_parser('introduce'); s.add_argument('--type', required=True, choices=mastery.TYPES)
    s.add_argument('--content', required=True); s.add_argument('--meaning', required=True)
    s.add_argument('--sense', default=''); s.add_argument('--note-id')
    s = k.add_parser('record'); s.add_argument('--id', required=True); s.add_argument('--attempt-id', required=True)
    s.add_argument('--mode', required=True, choices=['comprehension','application','transfer'])
    s.add_argument('--outcome', required=True, choices=mastery.OUTCOMES)
    s.add_argument('--assistance', required=True, choices=mastery.ASSISTANCE)
    for arg in ('context','question','feedback'):
        s.add_argument('--'+arg, required=True)
    s.add_argument('--answer', default='')
    c = sub.add_parser('cefr').add_subparsers(dest='action', required=True)
    for action in ('current','history','due','begin'):
        c.add_parser(action)
    s = c.add_parser('record'); s.add_argument('--id', required=True); s.add_argument('--item-id', required=True)
    s.add_argument('--skill', required=True, choices=e.SKILLS); s.add_argument('--difficulty', required=True, choices=e.LEVELS[:-1])
    for arg in ('question','answer','feedback'):
        s.add_argument('--'+arg, required=True)
    s.add_argument('--score', required=True, type=float); s.add_argument('--evidence-mode', choices=cefr.EVIDENCE, default='text')
    s = c.add_parser('finish'); s.add_argument('--id', required=True); s.add_argument('--summary', required=True)
    for skill in e.SKILLS:
        s.add_argument('--'+skill, required=True, choices=e.LEVELS)
    t = sub.add_parser('study').add_subparsers(dest='action', required=True)
    s = t.add_parser('begin'); s.add_argument('--id'); s.add_argument('--planned-minutes', type=int)
    s = t.add_parser('record'); s.add_argument('--id', required=True); s.add_argument('--activity-id', required=True)
    s.add_argument('--type', choices=study_time.ACTIVITIES, required=True); s.add_argument('--minutes', type=int, required=True)
    s = t.add_parser('finish'); s.add_argument('--id', required=True)
    duration = s.add_mutually_exclusive_group(required=True)
    duration.add_argument('--effective-minutes', type=int); duration.add_argument('--unknown', action='store_true')
    t.add_parser('history')
    s = t.add_parser('summary'); s.add_argument('--start'); s.add_argument('--end')
    a = sub.add_parser('analytics').add_subparsers(dest='action', required=True)
    for action in ('weekly','monthly','trends','difficulties'):
        a.add_parser(action)
    s = a.add_parser('summary'); s.add_argument('--start'); s.add_argument('--end')
    args = ap.parse_args(argv)
    base = root()
    try:
        if args.cmd in ('knowledge','cefr','study','analytics') and e.checked_config(base)['schema_version'] != 2:
            raise ValueError('Execute python -m tutor.cli migrate antes de usar os novos comandos')
        if args.cmd == 'migrate': show(migrations.migrate(base))
        elif args.cmd == 'knowledge':
            if args.action == 'list': show(list(mastery.items(base).values()))
            elif args.action == 'summary': show(mastery.summary(base))
            elif args.action == 'gaps': show(mastery.gaps(base))
            elif args.action == 'show': show(mastery.get(base,args.id))
            elif args.action == 'introduce':
                song_id = state(base).get('active_song')
                if song_id: e.check_thread(base, e.active_song(base)[0])
                item = mastery.introduce(base,args.type,args.content,args.meaning,sense=args.sense,
                                         song_id=song_id,note_id=args.note_id)
                if not song_id: review_policy.schedule(base,item['id'])
                show(item)
            else:
                song_id = state(base).get('active_song')
                if song_id: e.check_thread(base, e.active_song(base)[0])
                item = mastery.record(base,args.id,args.attempt_id,args.mode,args.outcome,args.assistance,
                                      args.context,args.question,args.answer,args.feedback,song_id=song_id)
                queue = read_json(base/'data/reviews.json', {})
                key = item.get('note_id') or item['id']
                if (not song_id or (key in queue and queue[key]['status']=='finished')) and item['status'] != 'consolidated':
                    review_policy.schedule(base,item['id'],song_id)
                show(item)
        elif args.cmd == 'cefr':
            if args.action == 'current': show(cefr.current(base))
            elif args.action == 'history': show(cefr.history(base))
            elif args.action == 'due': show(cefr.due(base))
            elif args.action == 'begin': show(cefr.begin(base))
            elif args.action == 'record':
                show(cefr.record(base,args.id,args.item_id,args.skill,args.difficulty,args.question,
                                 args.answer,args.score,args.feedback,args.evidence_mode))
            else: show(cefr.finish(base,args.id,{k:getattr(args,k) for k in e.SKILLS},args.summary))
        elif args.cmd == 'study':
            if args.action == 'begin':
                if state(base).get('active_song'): e.check_thread(base,e.active_song(base)[0])
                show(study_time.begin(base,args.planned_minutes,args.id))
            elif args.action == 'record': show(study_time.record(base,args.id,args.activity_id,args.type,args.minutes))
            elif args.action == 'finish': show(study_time.finish(base,args.id,args.effective_minutes))
            elif args.action == 'history': show(list(study_time.sessions(base).values()))
            else: show(study_time.summary(base,args.start,args.end))
        elif args.cmd == 'analytics':
            if args.action == 'summary': show(analytics.summary(base,args.start,args.end))
            elif args.action in ('weekly','monthly'): show(analytics.period(base,args.action))
            elif args.action == 'trends': show(analytics.trends(base))
            else: show(analytics.difficulties(base))
        elif args.cmd == 'doctor': show(doctor(base))
        elif args.cmd == 'status': show(e.metrics(base))
        elif args.cmd == 'onboard': onboard(base)
        elif args.cmd == 'diagnostic':
            if args.action == 'record':
                show(e.record_diagnostic(base, args.skill, args.difficulty, args.question,
                                         args.answer, args.score, args.feedback, args.evidence_mode))
            else:
                levels = {x: getattr(args, x) for x in e.SKILLS}
                show(e.finish_diagnostic(base, levels, args.summary))
        elif args.cmd == 'roadmap':
            if args.action == 'create': show(e.create_roadmap(base,args.reason))
            else: show(e.read_yaml(base / 'data/roadmap.yaml'))
        elif args.cmd == 'song':
            if args.action == 'start': show(e.start_song(base, args.title, args.artist, args.source))
            elif args.action == 'begin-day': show(e.begin_day(base, args.day))
            elif args.action == 'checkpoint': show(e.checkpoint(base, args.day, args.activity, args.evidence, args.feedback, args.score, skill=args.skill,difficulty=args.difficulty,error_tag=args.error_tag))
            elif args.action == 'end-day': show(e.end_day(base, args.day, args.summary))
            elif args.action == 'finish': show(e.finish_song(base, args.comprehension, args.expressions, args.pronunciation, args.speaking, args.summary))
            elif args.action == 'difficulty':
                from .store import write_json
                cycle,path = e.active_song(base); e.check_thread(base,cycle)
                if not args.evidence.strip(): raise ValueError('Informe evidência da dificuldade')
                cycle['difficulty'] = {'level':args.level,'evidence':args.evidence}; write_json(path/'cycle.json',cycle); show(cycle['difficulty'])
            else: show(e.active_song(base)[0])
        elif args.cmd == 'note':
            show(e.add_note(base, args.type, args.title, args.meaning, args.example,
                            args.evidence, [x.strip() for x in args.tags.split(',') if x.strip()]))
        elif args.cmd == 'review':
            if args.action == 'due': show(e.due_reviews(base, args.date))
            else: show(e.grade_review(base, args.note_id, args.result == 'correct', args.evidence, attempt_id=args.attempt_id, assistance=args.assistance, context=args.context, question=args.question, answer=args.answer))
        elif args.cmd == 'graph': show(graph_sync(base, args.source))
    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as exc:
        print('ERRO:', exc, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
