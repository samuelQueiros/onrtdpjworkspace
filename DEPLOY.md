# Deploy — ONRTDPJ Workspace

Guia de deploy do projeto via **Docker Compose** (local) e **Portainer** (produção, com deploy direto a partir do GitHub). Este documento também define o **padrão de deploy** a ser replicado nos demais sistemas internos (RH, Cancelador, Ouvidoria, ONRTDPJ Workspace e futuros projetos), para que todos sigam a mesma estrutura, variáveis e fluxo de operação.

> Para instalar o Docker no servidor, comandos de backup/restore e detalhes de cada serviço, veja também [docs/DOCKER-SERVIDOR.md](docs/DOCKER-SERVIDOR.md).

---

## Sumário

- [Arquitetura do deploy](#arquitetura-do-deploy)
- [Como subir localmente](#como-subir-localmente)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Como subir no Portainer](#como-subir-no-portainer)
- [Como atualizar a aplicação](#como-atualizar-a-aplicação)
- [Como fazer rollback](#como-fazer-rollback)
- [Padrão de deploy para novos projetos](#padrão-de-deploy-para-novos-projetos)

---

## Arquitetura do deploy

```text
                         ┌────────────────────────────┐
Internet / rede interna  │      Nginx Proxy Manager    │  (gerencia HTTPS/domínios de
        │                │   (fora deste repositório)  │   todos os projetos do servidor)
        ▼                └──────────────┬─────────────┘
                                         │ proxy_pass para o host:FRONTEND_PORT
                                         ▼
                         ┌────────────────────────────┐
                         │   frontend (Nginx + React)  │  porta publicada: FRONTEND_PORT
                         │   proxy interno /api/  ───┐ │
                         └────────────────────────────┼─┘
                                                       ▼
                         ┌────────────────────────────┐
                         │    backend (FastAPI)        │  porta publicada: BACKEND_PORT
                         └──────────────┬─────────────┘
                                        ▼
                         ┌────────────────────────────┐
                         │    db (PostgreSQL)          │  sem porta publicada
                         └────────────────────────────┘
```

- O frontend nunca chama o backend por IP/hostname fixo: ele usa `VITE_API_URL` (padrão `/api`), e o próprio Nginx do frontend encaminha `/api/*` para `http://backend:8000` internamente (rede Docker).
- O backend nunca tem a URL do frontend fixa no código: usa `FRONTEND_URL`/`CORS_ORIGINS` para liberar CORS.
- O **Nginx Proxy Manager (NPM)** fica fora deste `docker-compose.yml` (é uma stack própria, compartilhada por todos os projetos do servidor) e aponta para `http://chat-server:FRONTEND_PORT` — `chat-server` é o hostname já salvo (DNS/hosts) da máquina que roda o Portainer e é usado como endereço de acesso por todos os projetos internos.
- Como **todos os projetos (RH, Cancelador, Ouvidoria, ONRTDPJ Workspace, etc.) rodam no mesmo `chat-server`**, cada um precisa de `FRONTEND_PORT`/`BACKEND_PORT` únicos (veja a tabela de portas na seção de padronização) e `FRONTEND_URL` deve ser exatamente o endereço usado no navegador — `http://chat-server` quando a porta é 80, ou `http://chat-server:PORTA` caso contrário.

---

## Como subir localmente

### Opção A — Docker Compose (recomendado, igual à produção)

```bash
cp .env.example .env
# edite o .env (veja a seção Variáveis de Ambiente)

docker compose up --build -d
docker compose ps
docker compose logs -f
```

Acesso: `http://localhost` (frontend) e `http://localhost:8000/docs` (Swagger).

### Opção B — sem Docker (desenvolvimento ativo do código)

Veja [README.md — Rodando em Desenvolvimento (sem Docker)](README.md#rodando-em-desenvolvimento-sem-docker).

---

## Variáveis de ambiente

Todas as variáveis ficam em um único `.env` na raiz do projeto (nunca versionado). O arquivo [`.env.example`](.env.example) lista todas elas com comentários.

Resumo dos grupos:

| Grupo | Variáveis | Observação |
|---|---|---|
| Banco de dados | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `POSTGRES_PASSWORD` é obrigatório, sem valor padrão |
| Segurança do backend | `SECRET_KEY`, `CREDENTIALS_ENCRYPTION_KEY` | Obrigatórios em produção; gere com `python3 -c "import secrets; print(secrets.token_hex(48))"` |
| Sessão | `ACCESS_TOKEN_EXPIRE_MINUTES`, `COOKIE_SECURE` | `COOKIE_SECURE=true` somente atrás de HTTPS |
| Rede/CORS | `FRONTEND_URL`, `CORS_ORIGINS` | `FRONTEND_URL` é a origem principal liberada no CORS; `CORS_ORIGINS` (opcional, separado por vírgula) libera origens adicionais |
| Frontend | `VITE_API_URL` | Embutido no build do frontend — mudou? precisa rebuildar |
| Portas | `FRONTEND_PORT`, `BACKEND_PORT` | Portas publicadas no host; escolha valores únicos por projeto no mesmo servidor |
| Admin inicial | `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Só cria o admin se ainda não existir nenhum |
| Uploads | `UPLOAD_DIR` | Caminho interno do container (padrão `/app/uploads`) |

Nenhuma dessas variáveis fica com valor sensível dentro do `docker-compose.yml` — todas são lidas do ambiente/`.env`.

---

## Como subir no Portainer

Pré-requisitos: Portainer instalado no servidor, com acesso a um repositório Git **privado** deste projeto (HTTPS + usuário/token, ou chave SSH configurada no Portainer).

### 1. Criar a stack a partir do repositório (Repository deployment)

1. No Portainer, acesse **Stacks → Add stack**.
2. Em **Build method**, escolha **Repository**.
3. Preencha:
   - **Repository URL**: URL do repositório Git privado (ex.: `https://github.com/sua-org/onrtdpjworkspace.git`).
   - **Repository reference**: branch de produção (ex.: `refs/heads/main`).
   - **Authentication**: ative e informe usuário + Personal Access Token (ou configure uma credencial Git reutilizável em **Settings → Registries/Git credentials**).
   - **Compose path**: `docker-compose.yml` (raiz do repositório).
4. Em **Environment variables**, adicione as mesmas variáveis do `.env.example` (uma a uma pela UI, ou use **Advanced mode** para colar o conteúdo completo de um `.env` já preenchido).
5. Ative **GitOps updates** se quiser que o Portainer reaplique a stack automaticamente a cada push (webhook) — veja a seção [Como atualizar a aplicação](#como-atualizar-a-aplicação).
6. Clique em **Deploy the stack**.

O Portainer vai clonar o repositório, buildar as imagens de `backend/Dockerfile` e `frontend/Dockerfile` localmente no host Docker gerenciado, e subir os três serviços na ordem correta (o `backend` só inicia depois do `db` ficar `healthy`; o `frontend` só depois do `backend` ficar `healthy`).

### 2. Conferir o status

Em **Stacks → onrtdpjworkspace (ou o nome escolhido) → Containers**, todos os serviços devem aparecer como `healthy`. Os nomes dos containers são gerados automaticamente pelo Compose (não há `container_name` fixo), no formato `<nome-da-stack>-<serviço>-<n>`.

### 3. Publicar via Nginx Proxy Manager

No NPM, crie um **Proxy Host** apontando para `http://chat-server:FRONTEND_PORT` (o valor definido em `.env`/nas variáveis da stack), com o domínio público desejado e certificado SSL (Let's Encrypt), se houver um. Não é necessário abrir a `BACKEND_PORT` publicamente — o frontend já faz proxy interno de `/api`.

Se os usuários continuarem acessando diretamente por `http://chat-server:FRONTEND_PORT` (sem passar pelo NPM/domínio), lembre-se de manter `FRONTEND_URL` igual a esse endereço; se passar a existir também um domínio público via NPM, adicione-o em `CORS_ORIGINS` para liberar as duas origens.

---

## Como atualizar a aplicação

### Via Portainer (recomendado)

- **Manual**: na stack, clique em **Pull and redeploy** (ou **Update the stack**) — o Portainer busca o commit mais recente da branch configurada, rebuilda as imagens e recria os containers alterados, mantendo os volumes (`ferias_data` e a pasta `uploads/`) intactos.
- **Automático (webhook)**: com **GitOps updates** ativado, configure o webhook gerado pelo Portainer no repositório Git (Settings → Webhooks). Cada push na branch de produção dispara o redeploy automaticamente.

### Manual via SSH (alternativa)

```bash
cd /opt/onrtdpjworkspace
git pull
docker compose up -d --build
```

Migrations do banco (`alembic upgrade head`) rodam automaticamente na inicialização do `backend` — não é necessário nenhum passo manual adicional.

---

## Como fazer rollback

### 1. Rollback de código (mais comum)

```bash
# localizar o commit estável anterior
git log --oneline

# reverter a branch de produção para esse commit
git revert <hash-do-commit-problematico>
git push
```

No Portainer, rode **Pull and redeploy** (ou aguarde o webhook). Como as migrations do Alembic são incrementais, reverter o código normalmente é seguro **desde que o rollback não dependa de uma migration de banco já aplicada ser desfeita**.

### 2. Rollback de stack no Portainer

Em **Stacks → onrtdpjworkspace → Editor**, o Portainer mantém o histórico de versões do `docker-compose.yml`/variáveis aplicadas. É possível reverter para uma configuração anterior da stack e redeployar.

### 3. Rollback de banco de dados (quando uma migration precisa ser desfeita)

```bash
docker compose exec backend alembic downgrade -1
```

Ou restaure um backup completo — veja [scripts/backup.ps1 e scripts/restore.ps1](docs/DOCKER-SERVIDOR.md#backup-do-banco-e-documentos). **Sempre faça backup antes de qualquer rollback que envolva o banco.**

---

## Padrão de deploy para novos projetos

Esta estrutura é o padrão a ser replicado em qualquer novo sistema hospedado no mesmo servidor Portainer (RH, Cancelador, Ouvidoria, ONRTDPJ Workspace, etc.), para manter a manutenção previsível entre projetos:

```text
<projeto>/
|-- docker-compose.yml     # services: db (se aplicável), backend, frontend — sem container_name,
|                           #   com restart: unless-stopped, healthcheck e depends_on condition: service_healthy
|-- .env.example            # todas as variáveis documentadas, sem nenhum segredo real
|-- DEPLOY.md                # este mesmo roteiro: local / Portainer / atualizar / rollback
|-- backend/
|   |-- Dockerfile           # multi-stage (builder + runtime), usuário não-root, HEALTHCHECK
|   +-- .dockerignore
+-- frontend/
    |-- Dockerfile           # multi-stage (build Vite/Node + runtime Nginx), HEALTHCHECK
    |-- nginx.conf           # proxy interno /api -> backend, headers de segurança
    +-- .dockerignore
```

Convenções fixas entre projetos:

- **Sem segredos no `docker-compose.yml`**: tudo vem de variáveis de ambiente/`.env`; senhas e chaves obrigatórias usam `${VAR:?mensagem de erro}` para falhar rápido se esquecidas.
- **Sem `container_name` fixo**: o Compose/Portainer nomeia os containers pelo nome da stack.
- **Sem URLs fixas no código**: frontend sempre usa uma variável (`VITE_API_URL`) para achar a API; backend sempre usa variável (`FRONTEND_URL`/`CORS_ORIGINS`) para liberar CORS.
- **`FRONTEND_PORT`/`BACKEND_PORT` únicos por projeto**, para permitir múltiplas stacks publicadas atrás do mesmo Nginx Proxy Manager, todas no mesmo host (`chat-server`).
- **`FRONTEND_URL` sempre igual ao endereço usado no navegador**: `http://chat-server` quando a porta é 80, ou `http://chat-server:PORTA` nos demais casos — é esse valor que o backend compara com o header `Origin` para liberar o CORS.
- **Todo serviço com `HEALTHCHECK`** (no Dockerfile e/ou no compose) e `depends_on` usando `condition: service_healthy` quando a ordem de subida importa.
- **`restart: unless-stopped`** em todos os serviços de aplicação.
- Volumes/bind mounts só para o que precisa persistir de fato (banco de dados e arquivos enviados por usuários) — nada de volume para código ou build artifacts.

### Alocação de portas no `chat-server`

Como todos os projetos dividem o mesmo host, mantenha um registro simples das portas já usadas para evitar colisão ao criar uma nova stack no Portainer:

| Projeto | FRONTEND_PORT | BACKEND_PORT |
|---|---|---|
| ONRTDPJ Workspace (este) | `80` | `8000` |
| RH | _a definir_ | _a definir_ |
| Cancelador | _a definir_ | _a definir_ |
| Ouvidoria | _a definir_ | _a definir_ |

Sugestão de faixa: reserve blocos de 10 em 10 por projeto (ex.: `8010`/`8011`, `8020`/`8021`...) para deixar espaço para múltiplos serviços por projeto no futuro sem precisar reorganizar portas já publicadas.
