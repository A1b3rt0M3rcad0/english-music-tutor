# INSTALL.md — instalação do template, workspace, hooks e Graphify

Este documento descreve dois ambientes **separados**:

- **Template público:** código, scripts, skills, instruções e modelos. Deve continuar sem dados pessoais de estudo.
- **Workspace pessoal:** criado por `bootstrap.py` fora do template. Contém cópia executável das ferramentas e começa **sem músicas, avaliações e notas**. Pode ser um segundo repositório Git.

## 0. Pré-requisitos

- Python **3.10 ou superior** (`python --version` ou `py -3 --version`).
- Git (`git --version`) caso queira publicar no GitHub.
- Node.js/npm para instalar Codex CLI, caso ainda não possua.
- Codex CLI instalado e autenticado (consulte https://developers.openai.com/codex/cli/ ). O acesso ao modelo depende da sua conta/configuração.
- Graphify **opcional**, instalado de forma independente.

Instalação habitual de Codex CLI, se não estiver presente:

```bash
npm install -g @openai/codex
codex --version
codex login
```

Consulte o guia oficial para alternativas e versões compatíveis. Não coloque tokens em arquivos versionados.

## 1. Publicar o template público no GitHub (uma vez)

1. Extraia o ZIP para `english-music-tutor/` ou clone o repositório-fonte.
2. Entre nessa pasta e verifique `README.md`, `INSTALL.md`, `AGENTS.md`, `.agents/skills/` e `tutor/`.
3. Opcional: rode os testes (seção 5).
4. Crie um **repositório vazio público** no GitHub com o nome desejado, sem inicializar README remoto.
5. Execute os comandos, substituindo `SEU-USUARIO`:

```bash
git init
git branch -M main
git add .
git commit -m "chore: initial reusable music tutor template"
git remote add origin https://github.com/SEU-USUARIO/english-music-tutor.git
git push -u origin main
```

**Não abra o Codex para estudar dentro deste repositório público.** Este repositório é um modelo genérico, com `config.example.yaml` sem dados. Evite adicionar `config.yaml` pessoal aqui.

## 2. Criar workspace pessoal INDEPENDENTE

### Windows PowerShell

```powershell
cd C:\Projetos\english-music-tutor
py -3 bootstrap.py --workspace ..\meu-ingles
cd ..\meu-ingles
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m tutor.cli doctor
```

Caso PowerShell bloqueie ativação, utilize o executável diretamente sem alterar política global:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m tutor.cli doctor
```

No Windows, o hook versionado usa `py -3` para invocar um módulo que depende apenas da biblioteca padrão, mesmo quando a venv não estiver ativada. Os comandos de tutoria (`python -m tutor.cli ...`) exigem PyYAML instalado no Python em uso. Abra o Codex com a venv ativada.

### Linux / macOS

```bash
cd ~/projects/english-music-tutor
python3 bootstrap.py --workspace ../meu-ingles
cd ../meu-ingles
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m tutor.cli doctor
```

Se o destino já contiver arquivos, o bootstrap **aborta sem sobrescrever**. Se o caminho estiver dentro do template, também aborta. Isso protege contra misturar código público com dados pessoais.

## 3. Configurar e validar os hooks do Codex

O workspace já contém **`.codex/hooks.json`** com dois hooks:

| Evento | Comando | Finalidade |
|---|---|---|
| `SessionStart` (startup/resume/compact/fork/clear) | `python -m tutor.hooks start` | Carrega contexto curto: onboarding, diagnóstico, roadmap, música ativa e revisões vencidas. Salva identificador do chat, se fornecido pelo Codex. |
| `SessionEnd` | `python -m tutor.hooks end` | Marca encerramento consultivo; não inventa notas e não conclui sessões. |

O campo `commandWindows` utiliza `py -3 -m tutor.hooks start/end` no Windows. Hooks são **configurações por projeto**; não mexemos no `~/.codex/config.toml` do usuário.

**Ativação e confiança:**

1. Abra um terminal **na raiz do workspace pessoal**.
2. Rode `codex`.
3. Execute `/hooks` no CLI: revise o `hooks.json`, **confie** nos handlers que você verificou e habilite-os. O Codex pode ignorar hooks de projetos que ainda não foram marcados como confiáveis.
4. Inicie um novo chat e verifique se o agente identifica o estado correto. Se `/hooks` estiver indisponível, verifique a versão da sua instalação.
5. Se o Codex não executar hooks, o agente ainda pode operar: `AGENTS.md` exige leitura de `config.yaml`, `data/state.json`, `review due` e `song current` no início do chat.

**Teste local sem Codex** (na raiz do workspace):

```bash
python -m tutor.hooks start
python -m tutor.hooks end
```

`start` imprime JSON com `hookSpecificOutput.additionalContext` e `end` grava `.tutor/hook_last_end.json`. Os hooks não iniciam tarefas em background. `SessionEnd` pode ocorrer muito depois de você trocar de conversa; por isso, o agente precisa salvar checkpoints e notas **durante** cada sessão, não depender de uma automação de encerramento.

O Codex confere confiança pela definição do hook; mudanças exigem nova revisão. Não use `--dangerously-bypass-hook-trust` para instalação comum. Consulte https://learn.chatgpt.com/docs/hooks para o schema atual.

## 4. Instalar o Graphify opcional (no workspace PESSOAL)

O software externo é [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify); a distribuição Python correta é **`graphifyy`**, e o comando da ferramenta é `graphify`.

Com `uv` (recomendado):

```bash
uv tool install graphifyy
graphify --help
```

Alternativa: `pipx install graphifyy`. Instale o Graphify conforme o README oficial; funcionalidades de indexação semântica podem exigir um backend local (Ollama) ou remoto com credenciais próprias.

**Na raiz do workspace pessoal**, instale a skill oficial específica para Codex:

```bash
graphify install --project --platform codex
```

Isso coloca a skill oficial em `.agents/skills/graphify/` e pode acrescentar instruções ao `AGENTS.md`. **Revise o diff antes de commitar ou substituir instruções existentes**; preserve as regras de tutoria. O template já inclui a skill própria `graphify-navigation`, que funciona como política de consulta e fallback sem bundlar código Graphify.

Para gerar o índice apenas das anotações:

```bash
graphify ./data/notes
# ou, depois de backend configurado:
python -m tutor.cli graph sync
```

O `graphify-out/` é gerado e ignorado pelo Git. Veja `graphify query --help` para consultas na versão instalada. Não indexe o repositório-template público para construir grafo de conhecimento do aluno.

A integração é **opcional** e não interfere no registro ou nas revisões se o Graphify faltar. A execução de `graph sync` pode usar tokens/serviços pagos; o tutor deve informar isso, não disparar a indexação sem configuração/consentimento.

## 5. Validação da instalação

Na raiz do template:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q tutor bootstrap.py
```

Na raiz do workspace:

```bash
python -m tutor.cli doctor
python -m tutor.cli status
python -m tutor.hooks start
```

`doctor` informa se faltam Codex CLI, Graphify ou arquivos do projeto. O Graphify é **opcional**, portanto sua ausência não invalida a tutoria.

## 6. Primeira conversa: onboarding, nivelamento e roadmap

1. Abra `codex` na raiz de **`meu-ingles`**, não no template.
2. Diga: `Quero começar minha jornada de inglês com músicas.`
3. O agente lerá `AGENTS.md` e skill `onboarding`, perguntará **uma coisa de cada vez**: objetivo, duração (dias/contínua), dias/semana, **tempo por sessão** e sessões/dia, acesso a áudio e experiência prévia.
4. O agente gravará `config.yaml` e aplicará o diagnóstico inicial (gramática, vocabulário, reading, listening, writing e speaking se houver ferramentas).
5. Após pelo menos 10 questões com respostas registradas, emitirá relatório com limitações explícitas. Depois executará `roadmap create` e personalizará metas.
6. Em **um novo chat**, envie: `Quero estudar [música], de [artista]`. O agente executará os três dias interativos. No Dia 2 e 3 **retome o mesmo chat**.
7. Após o Dia 3, abra **novo chat para outra música**. O histórico permanece no disco e os hooks/AGENTS o recuperam.

Pode usar `python -m tutor.cli onboard` como fallback caso prefira preencher as perguntas no terminal, mas isso **não substitui o diagnóstico** feito pelo Codex.

## 7. Publicar SEU ambiente de estudo em OUTRO GitHub

Depois de criado `../meu-ingles`:

```bash
cd ../meu-ingles
git init
git branch -M main
git add .
git commit -m "chore: initialize private English learning workspace"
git remote add origin https://github.com/SEU-USUARIO/meu-ingles.git
git push -u origin main
```

**Recomenda-se criar `meu-ingles` como repositório privado.** `data/` será versionável se você quiser histórico Git, mas pode conter informações pessoais. Antes de publicar qualquer repositório, confira `git status` e `git diff --cached` para evitar divulgação indevida. O `.gitignore` já bloqueia `.env`, arquivos de áudio/letra, caches e saída de Graphify; ele **não** bloqueia as anotações pessoais do workspace, pois você pretende versionar seu histórico individual.

Não suba o ambiente pessoal para o repositório público de template. O código público permanece genérico e outros alunos criam seus próprios workspaces independentes.

## 8. Solução de problemas

- **`No module named yaml`:** use a venv em que executou `python -m pip install -e .`.
- **Hook não apareceu:** abra o projeto como confiável, confira `/hooks`, e inicie Codex na raiz do workspace.
- **Hook Windows falha:** cheque `py -3 --version` e `py -3 -m tutor.hooks start` na raiz.
- **`graphify: command not found`:** ajuste PATH com `uv tool update-shell` ou consulte documentação do Graphify.
- **`graph sync` falhou:** verifique credenciais/backend e tente `graphify ./data/notes` diretamente; notas seguem acessíveis em Markdown.
- **Música vinculada a outro chat:** volte ao chat original; o sistema previne compartilhar acidentalmente os três dias entre threads.
- **Tempo curto por sessão:** o agente distribui blocos e checkpoints entre sessões, sem afirmar que concluiu atividades não executadas.
- **Sem áudio:** pratique escuta em dispositivo externo e reporte execução; o agente não atribuirá avaliação de pronúncia sem gravação real.
- **Mudou de máquina:** clone o repositório pessoal, instale dependências e confie novamente nos hooks. IDs de chats antigos podem não estar disponíveis no novo cliente; preserve os checkpoints e retome com o agente conforme o caso, sem apagar evidências.
