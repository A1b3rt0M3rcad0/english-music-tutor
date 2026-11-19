"""Cria um workspace *independente* do repositório público, sem dados de aluno."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def create_workspace(destination: Path) -> Path:
    dest = destination.expanduser().resolve()
    if dest == ROOT or ROOT in dest.parents:
        raise ValueError('O workspace pessoal precisa ficar FORA do repositório-template.')
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f'Destino não vazio: {dest}. Escolha uma pasta nova.')
    dest.mkdir(parents=True, exist_ok=True)
    for folder in ('tutor', '.agents', '.codex', 'docs'):
        shutil.copytree(ROOT / folder, dest / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for filename in ('pyproject.toml', '.gitignore', '.graphifyignore', 'LICENSE', '.env.example'):
        shutil.copy2(ROOT / filename, dest / filename)
    shutil.copy2(ROOT / 'config.example.yaml', dest / 'config.yaml')
    shutil.copy2(ROOT / 'AGENTS.md', dest / 'AGENTS.md')
    shutil.copy2(ROOT / 'INSTALL.md', dest / 'INSTALL.md')
    (dest / 'data').mkdir(exist_ok=True)
    for folder in ('notes/expressions', 'notes/grammar', 'notes/pronunciation',
                   'notes/difficulties', 'assessments/placement', 'assessments/checkpoints',
                   'songs', 'sessions'):
        path = dest / 'data' / folder
        path.mkdir(parents=True, exist_ok=True)
        (path / '.gitkeep').touch()
    shutil.copy2(ROOT / 'docs' / 'WORKSPACE_README.md', dest / 'README.md')
    print(f'Workspace pessoal criado: {dest}')
    print('Próximos passos: cd <workspace> ; python -m pip install -e . ; python -m tutor.cli onboard')
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description='Cria ambiente de estudos independente')
    parser.add_argument('--workspace', required=True, help='Diretório novo, fora do template')
    args = parser.parse_args()
    create_workspace(Path(args.workspace))


if __name__ == '__main__':
    main()
