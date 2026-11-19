# English Music Tutor

Um tutor de inglês com música, conduzido pelo Codex. Ele faz o nivelamento, monta um plano de estudo conforme seu objetivo e registra o progresso para continuar de onde você parou.

## Começar

Você precisa de Python 3.10+ e Codex CLI instalado e autenticado.

```bash
git clone https://github.com/A1b3rt0M3rcad0/english-music-tutor.git
cd english-music-tutor
python3 -m venv .venv
.venv/bin/python -m pip install -e .
python3 bootstrap.py workspace
source .venv/bin/activate
codex
```

No Windows, use `py -3` e os comandos de ambiente virtual de `INSTALL.md`.

Quando o Codex abrir, diga **“Quero começar meus estudos de inglês com música.”** Ele conduz o onboarding, o nivelamento e o plano. Depois, peça uma música. Estude cada música no mesmo chat durante três dias efetivos e abra um chat novo para a próxima.

## Skills de estudo

O tutor também avalia a dificuldade linguística da música e testa o uso das expressões em situações novas. O Codex encontra essas skills automaticamente em uma nova sessão aberta na raiz do projeto. Veja [como elas funcionam](INSTALL-SKILLS.md).

## Seu progresso

O comando cria `workspaces/` dentro deste projeto. Configuração, notas e histórico ficam ali. O código, as instruções e os hooks são compartilhados na raiz. A pasta `workspaces/` é ignorada pelo Git para que seus dados não sejam enviados ao repositório público por acidente.

Se quiser guardar seu progresso no GitHub, use um repositório **privado** vazio. No diretório do projeto:

```bash
git remote add particular https://github.com/SEU_USUARIO/SEU_REPOSITORIO_PRIVADO.git
```

Remova a linha `/workspaces/` do `.gitignore` da raiz. Depois, adicione os dados e publique na primeira vez:

```bash
git add .gitignore workspaces
git commit -m "Salva meu progresso de estudo"
git push -u particular master
```

O comando `-u` direciona os próximos `git push` para o repositório particular. Confirme o endereço do remoto antes de enviar seu progresso. O `.gitignore` dentro de `workspaces/` continua excluindo credenciais, arquivos de áudio, a pasta `data/lyrics/` e arquivos temporários.

## Mais informações

- [Instalação no Windows, macOS e Linux](INSTALL.md)
- [Instruções do tutor](AGENTS.md)
- [Comandos e arquivos de progresso](docs/COMMANDS.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Skills de análise e transferência](INSTALL-SKILLS.md)

Graphify é opcional. Sem ele, notas e revisões continuam funcionando localmente. Recursos de áudio dependem do cliente e das ferramentas disponíveis. Não salve letras integrais protegidas por direitos autorais.
