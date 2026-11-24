"""Hooks Codex: estado conciso. Não extrai nem inventa anotações do transcript."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from .store import root, now, read_json, write_json


def hook_start(base: Path, payload: dict) -> dict:
    session_id = payload.get('session_id')
    directory = base / '.tutor'
    directory.mkdir(exist_ok=True)
    # A fonte de sessão é o evento Codex. Evita associar música a chat incorreto.
    if session_id:
        write_json(directory / 'session.json', {'session_id': session_id, 'at': now()})
    state = read_json(base / 'data/state.json', {})
    msg = ['Tutor de inglês. Leia AGENTS.md e workspaces/config.yaml antes de continuar.']
    if not (base / 'config.yaml').is_file():
        msg.append('Workspace ainda não iniciado. Quando o aluno quiser começar, execute python bootstrap.py workspace na raiz do projeto.')
    elif not state.get('onboarded'):
        msg.append('Aluno não configurado: conduza onboarding, uma pergunta por vez; registre em workspaces/config.yaml.')
    elif not state.get('diagnostic_done'):
        msg.append('Onboarding pronto. Faça diagnóstico progressivo antes de montar roadmap.')
    elif not state.get('roadmap_ready'):
        msg.append('Diagnóstico pronto. Crie roadmap de aprendizagem personalizado.')
    else:
        active = state.get('active_song')
        if active:
            cycle = read_json(base / 'data/songs' / active / 'cycle.json', {})
            other = cycle.get('thread_id') and session_id and cycle['thread_id'] != session_id
            msg.append(f'Música ativa: {active}, dia {cycle.get("day")}/3.' +
                       (' Atenção: chat diferente, retome thread original.' if other else ''))
        else:
            msg.append('Nenhuma música ativa. Novo chat pode iniciar uma nova música.')
        review = read_json(base / 'data/reviews.json', {})
        due = [v['note_id'] for v in review.values()
               if v.get('status') != 'finished' and v.get('due_date', '9999-99-99') <= now()[:10]]
        msg.append('Revisões vencidas: ' + (', '.join(due[:15]) if due else 'nenhuma'))
        from .store import read_yaml
        cfg = read_yaml(base/'config.yaml')
        if cfg.get('schema_version') == 2:
            from . import cefr, study_time
            if cefr.due(base)['due']: msg.append('Reavaliação CEFR pendente: consulte cefr due.')
            active_study = next((x for x in study_time.sessions(base).values() if x['status']=='active'),None)
            if active_study: msg.append('Retome sessão de estudo ativa: '+active_study['id'])
        elif cfg.get('schema_version') == 1:
            msg.append('Workspace v1: execute migrate com backup explícito antes de usar as métricas v2.')
    return {'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                   'additionalContext': '\n'.join(msg)}}


def hook_end(base: Path) -> None:
    # SessionEnd é consultivo e pode ocorrer muito depois da última mensagem.
    # Não considere a sessão concluída e não deduza respostas a partir de transcript instável.
    directory = base / '.tutor'
    directory.mkdir(exist_ok=True)
    write_json(directory / 'hook_last_end.json', {'at': now(), 'note': 'hook advisory only'})


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ('start', 'end'):
        print('Uso: python -m tutor.hooks start|end', file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except (ValueError, EOFError):
        payload = {}
    base = root()
    if sys.argv[1] == 'start':
        print(json.dumps(hook_start(base, payload), ensure_ascii=False))
    elif (base / 'config.yaml').is_file():
        hook_end(base)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
