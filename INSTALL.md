# Instalação

O tutor funciona neste único projeto. `python bootstrap.py workspace` cria a pasta `workspaces/` para suas preferências e seu progresso. O código e as skills permanecem na raiz.

## Requisitos

- Python 3.10 ou superior
- Codex CLI instalado e autenticado
- Git para clonar o projeto

## Windows PowerShell

Na pasta clonada:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
py -3 bootstrap.py workspace
.\.venv\Scripts\Activate.ps1
python -m tutor.cli doctor
codex
```

Se o PowerShell bloquear a ativação, use `.\.venv\Scripts\python.exe -m tutor.cli doctor` e abra o Codex a partir de um terminal com a venv ativa.

## macOS e Linux

Na pasta clonada:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
python3 bootstrap.py workspace
source .venv/bin/activate
python -m tutor.cli doctor
codex
```

No primeiro uso do Codex, execute `/hooks`, revise `.codex/hooks.json` e confie nos hooks do projeto. Se os hooks não estiverem habilitados, o tutor ainda pode ler o progresso em `workspaces/`.

## Graphify opcional

Graphify não é necessário para estudar. Se você quiser pesquisar relações entre suas notas, instale a ferramenta segundo a documentação oficial e a skill Codex com:

```bash
graphify install --project --platform codex
```

Revise as alterações feitas pelo instalador antes de aceitá-las. A indexação pode usar serviços remotos. Para atualizar o grafo configurado, execute `python -m tutor.cli graph sync` na raiz do projeto.

## Testes do projeto

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q tutor bootstrap.py
```

## Problemas comuns

- `No module named yaml`: ative a venv e instale o projeto com `python -m pip install -e .`.
- O tutor não encontra as preferências: na raiz do projeto, execute `python bootstrap.py workspace`.
- Um hook não executa: abra o projeto como confiável e revise-o com `/hooks`.
- Não há áudio disponível: listening e pronúncia acústica ficam sem avaliação até haver evidência de áudio.

O progresso em `workspaces/` é local e ignorado pelo Git público. O README explica como enviá-lo a um repositório particular, se você quiser.
