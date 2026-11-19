# English Music Tutor — tutor adaptativo de inglês por músicas com Codex

> Projeto-template público, reutilizável e **sem dados de alunos**. Instale um ambiente individual em **outro diretório/repositório** com um comando. Idioma da experiência pedagógica: português brasileiro, com prática crescente em inglês.

## Para que serve?

O projeto transforma Codex em um **tutor interativo de inglês orientado por músicas**, com objetivo e prazo configuráveis (inclusive estudo contínuo), nivelamento inicial, roadmap dinâmico, sessões guiadas, exercícios, correções, retestes, anotações automáticas, revisões espaçadas e navegação opcional por grafo de conhecimento via Graphify.

O aluno decide onde quer chegar, em quanto tempo, quantas vezes por semana estudará, quantas sessões fará por dia e quanto tempo terá por sessão. O agente estima o número de músicas a partir da capacidade disponível, explica o nível de confiança dessa previsão e replaneja diante do desempenho.

## Experiência do aluno

1. **Primeiro chat:** o Codex realiza onboarding *uma pergunta por vez*, guarda escolhas em `config.yaml` e aplica nivelamento progressivo (A1–C2, por competência; áudio só quando realmente disponível).
2. **Roadmap:** o agente projeta fases e metas com base no diagnóstico, na disponibilidade e no objetivo; não promete um CEFR em prazo irreal.
3. **Novo chat para cada música:** o aluno envia título, artista e acesso à música/letra. Cada chat se concentra em **uma música** durante **três dias efetivos de estudo**.
4. **Dia 1 — Entender:** escuta, interpretação, 5–8 expressões, canto com letra, conversação.
5. **Dia 2 — Reproduzir:** ditado, shadowing, reconhecimento auditivo, canto e conversação.
6. **Dia 3 — Dominar:** compreensão independente, recall de expressões, canto de memória, produção livre e avaliação.
7. **Ciclo adaptativo permanente:** o agente instrui, testa, valida a resposta, adapta os exercícios e retesta. Apresenta **uma atividade por vez**.
8. **Memória automática:** o agente salva notas, respostas, erros, exemplos e checkpoints; o aluno **não precisa organizar caderno**.
9. **Revisões:** recuperação ativa D+1, D+3, D+7, D+14 e D+30, com reforço no dia seguinte ao erro. Em dias sem estudo, fica pendente.
10. **Graphify (opcional):** consultas de relações entre músicas, expressões, conceitos e dificuldades usando um grafo *derivado* das notas locais.

### Referência de sessão de duas horas

| Bloco diário | Tempo |
|---|---:|
| Revisões | 20 min |
| Música do dia (atividades específicas do Dia 1, 2 ou 3) | 60 min |
| Conversação | 30 min |
| Consolidação de notas pelo agente | 10 min |

Outros tempos são configuráveis; a agenda é reequilibrada de forma explícita. O tutor não simula um cronômetro real nem recursos de áudio indisponíveis.

## Quickstart — criar um ambiente de estudo SEPARADO

**Requisitos:** Python 3.10+, Git (recomendado), Codex CLI e acesso/autenticação ao modelo do Codex. Graphify é opcional. Veja **[INSTALL.md](INSTALL.md)** para Windows, Linux/macOS, hooks, confiança e Graphify.

```bash
# 1. Baixe ou clone este repositório público
# 2. Ainda na raiz do template, execute:
python bootstrap.py --workspace ../meu-ingles

# 3. Vá à NOVA pasta (fora do projeto-template)
cd ../meu-ingles
python -m pip install -e .
python -m tutor.cli doctor

# 4. Inicie o Codex NESTA pasta
codex
```

Na primeira conversa, diga: **`Quero começar meus estudos de inglês com música.`** O Codex conduz o onboarding e depois o nivelamento. Quando quiser iniciar uma música, abra novo chat e diga: **`Quero estudar [título] — [artista].`** No segundo e terceiro dias, **retome o mesmo chat**.

No Windows PowerShell, veja `INSTALL.md` para criação/ativação de ambiente virtual e comandos equivalentes.

## Dois repositórios, responsabilidades distintas

```text
english-music-tutor/         # Repositório PÚBLICO template (GitHub)
  README.md
  INSTALL.md
  AGENTS.md
  bootstrap.py
  config.example.yaml         # SEM dados pessoais
  .agents/skills/            # Skills reutilizáveis
  .codex/hooks.json          # Hooks versionados e auditáveis
  tutor/                     # Ferramentas locais
  tests/                     # Testes do template

meu-ingles/                   # OUTRO repositório (pessoal)
  AGENTS.md
  config.yaml                 # Configuração particular, criada vazia
  .agents/skills/
  .codex/hooks.json
  tutor/
  data/                       # Começa VAZIO; história aparece durante estudo
  graphify-out/               # Gerado localmente, ignorado pelo git
```

O bootstrap **não inicializa Git**, não faz commit e não publica nada. Você escolhe se o repositório pessoal será privado; para informações de progresso e experiências pessoais, **privado é recomendado**. Alterar o template público não modifica automaticamente os workspaces já criados; para atualizar, aplique um processo de migração/rebase consciente, preservando dados.

## Skills nativas

As instruções de agente são organizadas em `.agents/skills/<nome>/SKILL.md`: `onboarding`, `placement-assessment`, `learning-roadmap`, `music-study-coach`, `lyrics-comprehension`, `pronunciation-shadowing`, `speaking-coach`, `learning-assessment`, `adaptive-learning`, `automatic-notes`, `spaced-repetition`, `graphify-navigation`.

`AGENTS.md` determina quando utilizar cada skill e como encadear exercícios. Os scripts são apenas persistência/cálculo; o **Codex** realiza as análises e a tutoria. O Graphify oficial é instalado separadamente, não copiado dentro do repositório.

## Privacidade, áudio e direitos autorais

- **Não salva letras completas** nem arquivos de áudio protegidos no template. A conversa pode conter conteúdo enviado pelo aluno para estudo pessoal; o agente persiste metadados, notas próprias, referências e trechos curtos necessários quando autorizado.
- **O repositório pessoal contém dados particulares** como exemplos escritos, erros e desempenho. Evite publicá-lo sem revisão.
- **Modo texto não avalia pronúncia nem fluência acústica.** A prática oral exige áudio/cliente compatível ou ferramenta externa. A pontuação de speaking/ listening fica não verificada se não houver evidência.
- O Codex e Graphify podem utilizar serviços remotos; “armazenamento local” não significa processamento integralmente offline.
- O Graphify pode exigir backend/modelo configurado. Sem ele, todas as notas e revisões funcionam em Markdown/JSON.

## Contribuições e validação

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q tutor bootstrap.py
```

Contribuições são bem-vindas; não inclua histórico de aprendizagem ou letras protegidas em issues/PRs. Licença do código-base: MIT (`LICENSE`). Integrações de terceiros mantêm suas respectivas licenças.

Documentos: [Instalação completa](INSTALL.md) · [Contrato do tutor](AGENTS.md) · [Comandos de persistência](docs/COMMANDS.md) · [Arquitetura](docs/ARCHITECTURE.md).
