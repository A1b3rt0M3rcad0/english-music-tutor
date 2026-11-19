"""Inicializa o workspace local dentro deste repositório."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def preserve_current_session(project: Path, workspace: Path) -> None:
    source = project / '.tutor' / 'session.json'
    target = workspace / '.tutor' / 'session.json'
    if source.is_file() and not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def create_workspace(project_root: Path = ROOT) -> Path:
    """Cria workspaces/ sem copiar o código compartilhado nem sobrescrever dados."""
    project = project_root.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f'Diretório do projeto não encontrado: {project}')

    dest = project / 'workspaces'
    if dest.is_symlink():
        raise ValueError('workspaces precisa ser uma pasta local, não um link simbólico.')
    if dest.exists():
        initialized = (dest / 'config.yaml').is_file() and (dest / 'data').is_dir()
        if initialized:
            preserve_current_session(project, dest)
            print(f'Workspace já existe e foi preservado: {dest}')
            return dest
        if any(dest.iterdir()):
            raise FileExistsError(f'{dest} já contém arquivos. Revise-os antes de inicializar.')

    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'config.yaml').write_text(
        (ROOT / 'config.example.yaml').read_text(encoding='utf-8'), encoding='utf-8')
    (dest / 'README.md').write_text(
        (ROOT / 'docs' / 'WORKSPACE_README.md').read_text(encoding='utf-8'), encoding='utf-8')
    (dest / '.gitignore').write_text(
        '# Dados pessoais e arquivos locais do workspace\n'
        '.env\n.env.*\n!.env.example\n'
        '.venv/\n__pycache__/\n*.py[cod]\n.pytest_cache/\n*.egg-info/\n'
        '.tutor/\n.graphify/\ngraphify-out/\n'
        'data/lyrics/\ndata/audio/\n'
        '*.mp3\n*.wav\n*.m4a\n*.mp4\n'
        '.DS_Store\nThumbs.db\n',
        encoding='utf-8')
    (dest / 'data').mkdir(exist_ok=True)
    for folder in ('notes/expressions', 'notes/grammar', 'notes/pronunciation',
                   'notes/difficulties', 'assessments/placement', 'assessments/checkpoints',
                   'songs', 'sessions'):
        path = dest / 'data' / folder
        path.mkdir(parents=True, exist_ok=True)
        (path / '.gitkeep').touch()
    preserve_current_session(project, dest)
    print(f'Workspace pessoal criado: {dest}')
    print('Próximo passo: abra o Codex na raiz do projeto e diga que quer começar a estudar.')
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description='Inicializa o workspace local do tutor')
    parser.add_argument('action', choices=['workspace'], help='Inicializa workspaces/ dentro do projeto')
    parser.parse_args()
    create_workspace()


if __name__ == '__main__':
    main()
