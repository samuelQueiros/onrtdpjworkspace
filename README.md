# ONRTDPJ Workspace — Sistema de Gestão RH

> Plataforma web interna do **Operador Nacional de Registro de Títulos e Documentos e Pessoas Jurídicas (ONRTDPJ)** para centralizar processos administrativos: gestão de férias, controle de acessos, comunicados internos, documentos e relatórios gerenciais — tudo em um único ambiente.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Módulos](#módulos)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Rodando em Desenvolvimento (sem Docker)](#rodando-em-desenvolvimento-sem-docker)
- [Deploy em Servidor com Docker](#deploy-em-servidor-com-docker)
- [Testes](#testes)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Credenciais Iniciais](#credenciais-iniciais)
- [Rotas do Frontend](#rotas-do-frontend)
- [Referência da API](#referência-da-api)
- [Modelos do Banco de Dados](#modelos-do-banco-de-dados)
- [Regras de Negócio](#regras-de-negócio)
- [Solução de Problemas](#solução-de-problemas)

---

## Visão Geral

O **ONRTDPJ Workspace** é um sistema web full-stack desenvolvido internamente para apoiar a gestão de pessoas e operações administrativas da organização. Substituindo planilhas e processos manuais, a plataforma oferece:

- Interface moderna com glassmorphism, totalmente responsiva
- Autenticação JWT com controle de perfis (Administrador / Colaborador)
- Banco de dados PostgreSQL com schema versionado por migrations Alembic
- Containerização completa via Docker e Docker Compose
- Backend executado como usuário não-root no container
- API RESTful documentada via Swagger (FastAPI)
- Notificações globais e modal de confirmação reutilizável para ações importantes

---

## Módulos

### Para todos os colaboradores

| Módulo | Descrição |
|--------|-----------|
| **Dashboard pessoal** | Saldo de dias, dias usados, próximas férias e alertas pessoais |
| **Gestão de Férias** | Solicitação, edição e cancelamento de períodos de férias com validações automáticas |
| **Disponibilidade** | Calendário visual com cores por colaborador para identificar sobreposições |
| **Mural de Avisos** | Comunicados internos com suporte a fixação e expiração automática |
| **Documentos** | Upload e download de atestados e documentos pessoais |
| **Autorizações de equipamentos** | Solicitação de itens vinculados ou disponíveis, acompanhamento, aceite e acesso ao termo definitivo |
| **Meus equipamentos** | Consulta dos patrimônios atualmente sob responsabilidade do colaborador |
| **Minhas Credenciais** | Visualização das credenciais de sistemas compartilhados que o colaborador tem acesso, com opção de copiar e mostrar/ocultar senhas |

Os documentos são armazenados em pasta persistente configurada por `UPLOAD_DIR`. Contracheques enviados por administradores ficam somente em `enviados/nome-administrador/nome-colaborador/arquivo`; atestados ficam somente em `recebidos/nome-colaborador/arquivo`. Cada upload gera uma única cópia física.

### Exclusivo para Administradores

| Módulo | Descrição |
|--------|-----------|
| **Dashboard Admin** | Visão consolidada: colaboradores ativos, aprovações pendentes, pessoas em férias hoje, próximas férias em 30 dias e central de alertas |
| **Aprovação de Férias** | Aprovação e rejeição com histórico completo (quem aprovou/rejeitou e quando) |
| **Usuários** | Cadastro e edição de colaboradores com cor identificadora, departamento, admissão e aniversário |
| **Departamentos** | Criação e edição de departamentos com configuração de limite simultâneo de férias |
| **Bloqueio de Datas** | Cadastro de períodos de bloqueio (ex.: auditoria) e recessos coletivos |
| **Acessos / Senhas** | Gerenciamento de credenciais compartilhadas (sistemas externos, painéis, etc.) com controle granular de acesso por colaborador |
| **Relatórios** | Relatório consolidado por colaborador exportável |
| **Logs do Sistema** | Auditoria completa de todas as ações com exportação em CSV |
| **Configurações** | Catálogo administrativo de cargos, com criação, edição e desativação de vínculos |
| **Patrimônios** | Inventário, vínculos históricos, manutenção, baixa e disponibilidade de equipamentos |
| **Autorizações de equipamentos** | Aprovação integral/parcial, rejeição, entrega, PDF, regeneração e devolução |

### Segurança e integridade

- A sessão web usa cookie JWT `HttpOnly` e `SameSite=Lax`.
- Contas criadas ou com senha redefinida por um administrador devem substituir
  a senha temporária no primeiro acesso antes de usar os demais módulos.
- Trocas de senha e logout global revogam tokens emitidos anteriormente.
- Endereços novos/atualizados e dados bancários são criptografados em repouso com `CREDENTIALS_ENCRYPTION_KEY`; endereços legados continuam legíveis para migração gradual.
- CPFs são validados, cifrados em repouso e possuem índice HMAC para impedir duplicidade sem expor o valor.
- O HTML histórico dos termos de equipamentos também é cifrado em repouso e usado na regeneração idempotente do PDF.
- Colaboradores são desativados em vez de excluídos, preservando histórico e documentos.
- Alterações concorrentes de férias são serializadas no PostgreSQL.
- Login possui limitação de tentativas por origem.
- Uploads possuem validação de assinatura e limites de tamanho.

O frontend publicado pelo Docker acessa a API pelo proxy interno `/api`. Para instalações HTTP controladas, configure `COOKIE_SECURE=false` junto de `ALLOW_INSECURE_PRODUCTION_COOKIE=true`; em produção com HTTPS, use `COOKIE_SECURE=true`.

---

## Tecnologias

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Backend** | Python + FastAPI | 3.12 / 0.110+ |
| **ORM** | SQLAlchemy | 2.x |
| **Banco de Dados** | PostgreSQL | 16 |
| **Autenticação** | JWT via `PyJWT` + hash `bcrypt` | — |
| **Feriados** | `holidays` (calendário oficial brasileiro) | — |
| **PDF e templates** | Jinja2 + WeasyPrint | 3.1.6 / 69.0 |
| **Frontend** | React + Vite | 18.3.1 / 8.1.3 |
| **Roteamento** | React Router | 6.30.4 |
| **Estilo** | CSS puro com design system de variáveis | — |
| **HTTP Client** | Fetch API nativa | — |
| **Servidor Web** | Nginx (produção) | 1.27-alpine |
| **Containerização** | Docker + Docker Compose | — |

---

## Estrutura do Projeto

```
feriasonr/
|-- docker-compose.yml              # Orquestra db + backend + frontend
|-- .env.docker.example             # Exemplo de variaveis para Docker
|-- README.md
|
|-- backend/
|   |-- Dockerfile                  # Imagem Python/FastAPI com usuario nao-root
|   |-- requirements.txt
|   |-- alembic.ini
|   |-- alembic/                    # Migrations versionadas do banco
|   |-- tests/                      # Testes unitarios do backend
|   +-- app/
|       |-- main.py                 # Entrypoint FastAPI, CORS, routers e startup
|       |-- database.py             # Engine/session SQLAlchemy
|       |-- core/                   # Configuracao, seguranca e criptografia
|       |-- models/                 # Modelos SQLAlchemy
|       |-- repositories/           # Acesso a dados
|       |-- routers/                # Rotas HTTP FastAPI
|       |-- schemas/                # DTOs/Pydantic de request/response
|       |-- services/               # Regras de negocio
|       +-- storage/                # Persistencia fisica de documentos
|
|-- frontend/
|   |-- Dockerfile                  # Build Vite e publicacao em Nginx
|   |-- nginx.conf                  # SPA fallback, cache e headers basicos
|   |-- package.json
|   |-- index.html
|   +-- src/
|       |-- main.jsx
|       |-- App.jsx                 # Providers globais e roteamento base
|       |-- index.css               # Importa os arquivos de estilos globais
|       |-- components/             # Componentes por dominio da interface
|       |   |-- aprovacoes/
|       |   |-- bloqueios/
|       |   |-- comum/
|       |   |-- credenciais/
|       |   |-- departamentos/
|       |   |-- disponibilidade/
|       |   |-- documentos/
|       |   |-- estrutura/
|       |   |-- login/
|       |   |-- logs/
|       |   |-- minhasCredenciais/
|       |   |-- minhasFerias/
|       |   |-- mural/
|       |   |-- painel/
|       |   |-- relatorios/
|       |   |-- solicitacaoFerias/
|       |   +-- usuarios/
|       |-- contexts/               # Auth, toast e confirmacao global
|       |-- layouts/                # Layout principal da aplicacao
|       |-- pages/                  # Containers de tela/rota
|       |-- routes/                 # Declaracao das rotas React Router
|       |-- services/               # Cliente HTTP e servicos por dominio
|       |   +-- dominios/
|       |-- styles/                 # base, layout, ui, login, features, responsive, effects
|       +-- utils/                  # Formatadores, validacoes e exportadores CSV
|
+-- uploads/                        # Criada em runtime; nao versionar
    |-- enviados/
    |-- recebidos/
    +-- termos-equipamentos/
```

---

## Rodando em Desenvolvimento (sem Docker)

### Pré-requisitos

- **Python 3.12+** com `pip`
- **Node.js 20+** com `npm`
- **PostgreSQL 14+** rodando localmente **ou** Docker instalado para subir apenas o banco

### 1. Subir o banco de dados

**Opção A — PostgreSQL já instalado localmente:**
```bash
createdb ferias
createuser ferias --pwprompt   # senha: ferias
psql -c "GRANT ALL PRIVILEGES ON DATABASE ferias TO ferias;"
```

**Opção B — Subir apenas o container do Postgres (recomendado):**
```bash
docker run -d \
  --name ferias-db \
  -e POSTGRES_USER=ferias \
  -e POSTGRES_PASSWORD=ferias \
  -e POSTGRES_DB=ferias \
  -p 127.0.0.1:5432:5432 \
  postgres:16-alpine
```

### 2. Backend

```bash
# Entrar na pasta
cd backend

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# .\venv\Scripts\Activate.ps1    # Windows PowerShell

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo de configuração
cp .env.example .env
# Edite o .env se necessário (veja seção Variáveis de Ambiente)

# Aplicar migrations do banco
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> **O banco é configurado por migrations Alembic**. O usuário administrador inicial é inserido no startup se não existir e se `ADMIN_EMAIL`/`ADMIN_PASSWORD` estiverem configurados.

Backend disponível em: `http://127.0.0.1:8000`  
Swagger (docs interativo): `http://127.0.0.1:8000/docs`

### 3. Frontend

Em um segundo terminal:

```bash
cd frontend

# Instalar dependências
npm install

# Criar .env apontando para o backend local
echo "VITE_API_URL=http://127.0.0.1:8000" > .env

# Iniciar servidor de desenvolvimento
npm run dev
# ou: npx vite
```

Frontend disponível em: `http://127.0.0.1:5173`

---

## Testes

Os testes automatizados do backend ficam em `backend/tests` e cobrem regras críticas de autenticação, usuários, férias, documentos, armazenamento físico de arquivos, credenciais criptografadas, relatórios, schemas/DTOs, repositórios e services.

Para executar usando Docker:

```bash
docker compose build backend
docker compose run --rm --entrypoint python backend -m unittest discover -s tests
```

Para executar localmente, instale antes as dependencias do backend:

```bash
cd backend
pip install -r requirements.txt
python -m unittest discover -s tests
```

---

## Deploy em Servidor com Docker

Esta é a forma recomendada para ambientes de produção ou staging. O `docker-compose.yml` orquestra três serviços: **banco de dados (PostgreSQL)**, **backend (FastAPI)** e **frontend (React + Nginx)**.

### Pré-requisitos no servidor

- Docker Engine 24+
- Docker Compose v2 (`docker compose` — sem hífen)
- Pelo menos **1 GB de RAM** disponível
- Porta **80** liberada no firewall; a porta **8000** do backend fica restrita
  ao loopback do servidor

### Passo a passo

#### 1. Enviar o código para o servidor

```bash
# Opção A: via git clone
ssh usuario@IP_DO_SERVIDOR
git clone https://seu-repositorio/feriasonr.git
cd feriasonr

# Opção B: via scp
scp -r ./feriasonr usuario@IP_DO_SERVIDOR:/opt/feriasonr
ssh usuario@IP_DO_SERVIDOR
cd /opt/feriasonr
```

#### 2. Criar o arquivo de variáveis de ambiente

Na raiz do projeto, crie o arquivo `.env`:

```bash
nano .env
```

Conteúdo mínimo recomendado para produção:

```env
# ── Banco de dados ─────────────────────────────
POSTGRES_USER=ferias
POSTGRES_PASSWORD=SenhaForteAqui123
POSTGRES_DB=ferias

# ── Backend ────────────────────────────────────
# OBRIGATÓRIO: troque por uma string aleatória longa
ENVIRONMENT=production
SECRET_KEY=cole-aqui-uma-chave-de-64-caracteres-ou-mais-gerada-aleatoriamente
CREDENTIALS_ENCRYPTION_KEY=cole-aqui-outra-chave-longa-para-criptografar-credenciais
ACCESS_TOKEN_EXPIRE_MINUTES=480
COOKIE_SECURE=false
ALLOW_INSECURE_PRODUCTION_COOKIE=true
TRUSTED_PROXY_IPS=172.16.0.0/12
BACKEND_PORT=8000
UPLOAD_DIR=/app/uploads
ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=troque-por-uma-senha-forte

# ── Frontend ───────────────────────────────────
# Troque pelo IP ou domínio público do servidor
VITE_API_URL=/api
FRONTEND_URL=http://SEU_IP_OU_DOMINIO
FRONTEND_PORT=80
```

> **Dica:** gere uma `SECRET_KEY` segura com:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(48))"
> ```

#### 3. Construir e subir os containers

```bash
# Construir as imagens e iniciar em background
docker compose up --build -d
```

Se estiver em servidor Linux, garanta que a pasta de uploads exista e permita escrita para o UID/GID `1000` usado pelo backend:

```bash
mkdir -p uploads
chown -R 1000:1000 uploads
chmod 775 uploads
```

Aguarde o processo concluir (~2-3 minutos na primeira vez). O Docker irá:
1. Baixar as imagens base (`postgres:16-alpine`, `python:3.12-slim`, `node:20-alpine`, `nginx:1.27-alpine`)
2. Instalar as dependências Python e Node
3. Fazer o build de produção do React
4. Copiar os arquivos estáticos para o Nginx
5. Executar as migrations em um container `migrate` de execução única
6. Iniciar o backend somente se as migrations terminarem com sucesso

#### 4. Verificar o status dos serviços

```bash
# Ver status dos containers
docker compose ps

# Saída esperada:
# NAME              STATUS          PORTS
# ferias-db         Up (healthy)    5432/tcp
# ferias-backend    Up              127.0.0.1:8000->8000/tcp
# ferias-frontend   Up              0.0.0.0:80->80/tcp
```

```bash
# Ver logs em tempo real
docker compose logs -f

# Logs apenas do backend
docker compose logs -f backend

# Logs apenas do banco
docker compose logs -f db
```

#### 5. Acessar o sistema

| Serviço | URL |
|---------|-----|
| **Frontend** (sistema web) | `http://SEU_IP_OU_DOMINIO` |
| **API interna** | `http://127.0.0.1:8000` no servidor |
| **Health check** | `http://127.0.0.1:8000/health/ready` no servidor |

#### 6. Manutenção

```bash
# Parar todos os serviços (mantém os dados)
docker compose stop

# Reiniciar
docker compose restart

# Atualizar após mudança de código
docker compose up --build -d

# Ver uso de recursos
docker stats

# Acessar o banco de dados pela rede interna do Docker
docker compose exec db psql -U ferias -d ferias

# Backup e restauração segura (PowerShell)
.\scripts\backup.ps1
.\scripts\restore.ps1 -BackupFile .\backups\ferias-AAAAMMDD-HHMMSS.zip
```

#### 7. Configurar domínio com HTTPS (Nginx Proxy + Certbot)

Para usar um domínio próprio com HTTPS, a abordagem recomendada é colocar um **Nginx reverso** na frente:

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seudominio.com.br

# Exemplo de configuração Nginx reverso (/etc/nginx/sites-available/ferias)
```

```nginx
server {
    listen 80;
    server_name seudominio.com.br;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name seudominio.com.br;
    client_max_body_size 11m;

    ssl_certificate     /etc/letsencrypt/live/seudominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com.br/privkey.pem;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Variáveis de Ambiente

### Raiz do projeto — `.env` (usado pelo Docker Compose)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_USER` | Usuário do banco | `ferias` |
| `POSTGRES_PASSWORD` | Senha do banco | `ferias` |
| `POSTGRES_DB` | Nome do banco | `ferias` |
| `ENVIRONMENT` | Ambiente da aplicação (`production` no Docker) | `production` |
| `SECRET_KEY` | Chave de assinatura JWT (**trocar em produção!**) | `troque-esta-chave-em-producao` |
| `CREDENTIALS_ENCRYPTION_KEY` | Chave usada para criptografar senhas compartilhadas | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração da sessão em minutos | `480` (8h) |
| `COOKIE_SECURE` | Exige HTTPS para o cookie de sessão | `true` em HTTPS; `false` em HTTP controlado |
| `ALLOW_INSECURE_PRODUCTION_COOKIE` | Autoriza explicitamente cookie HTTP em rede controlada | `false` |
| `TRUSTED_PROXY_IPS` | Redes dos proxies autorizados a informar o IP real | `172.16.0.0/12` no Compose |
| `ADMIN_NAME` | Nome do administrador inicial criado no primeiro startup | `Administrador` |
| `ADMIN_EMAIL` | E-mail do administrador inicial | — |
| `ADMIN_PASSWORD` | Senha do administrador inicial | — |
| `VITE_API_URL` | URL usada pelo frontend para acessar a API | `/api` no Docker |
| `FRONTEND_URL` | URL do frontend (CORS) | `http://chat-server` |
| `BACKEND_PORT` | Porta exposta do backend | `8000` |
| `FRONTEND_PORT` | Porta exposta do frontend | `80` |
| `UPLOAD_DIR` | Pasta interna onde documentos enviados sao salvos | `/app/uploads` |
| `DATABASE_POOL_SIZE` | Conexões persistentes por processo do backend | `10` |
| `DATABASE_MAX_OVERFLOW` | Conexões extras temporárias por processo | `20` |
| `DATABASE_POOL_TIMEOUT_SECONDS` | Espera máxima por conexão livre | `30` |
| `DATABASE_POOL_RECYCLE_SECONDS` | Reciclagem preventiva de conexões | `1800` |
| `DATABASE_CONNECT_TIMEOUT_SECONDS` | Timeout ao abrir conexão com PostgreSQL | `10` |
| `DATABASE_STATEMENT_TIMEOUT_MS` | Timeout de cada comando SQL | `30000` |

### Backend — `backend/.env` (desenvolvimento local)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `ENVIRONMENT` | Ambiente da aplicação | `development` |
| `SECRET_KEY` | Chave JWT | — |
| `CREDENTIALS_ENCRYPTION_KEY` | Chave usada para criptografar senhas compartilhadas | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração da sessão | `480` |
| `DATABASE_URL` | URL completa do PostgreSQL | `postgresql://ferias:ferias@localhost:5432/ferias` |
| `UPLOAD_DIR` | Pasta local para salvar documentos enviados | `./data/uploads` |
| `ADMIN_NAME` | Nome do administrador inicial | `Administrador` |
| `ADMIN_EMAIL` | E-mail do administrador inicial | — |
| `ADMIN_PASSWORD` | Senha do administrador inicial | — |

### Frontend — `frontend/.env` (desenvolvimento local)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `VITE_API_URL` | URL base da API | `http://127.0.0.1:8000` |

---

## Credenciais Iniciais

O administrador inicial pode ser criado automaticamente se as variáveis ADMIN_EMAIL e ADMIN_PASSWORD forem configuradas antes da primeira inicialização.

| Campo | Valor |
|-------|-------|
| E-mail | Definido em `ADMIN_EMAIL` |
| Senha | Definida em `ADMIN_PASSWORD` |
| Perfil | Administrador |

> Use uma senha forte ja no `.env` de producao. O arquivo `.env` nao deve ser versionado.

---

## Rotas do Frontend

| Rota | Acesso | Descrição |
|------|--------|-----------|
| `/login` | Público | Tela de autenticação |
| `/alterar-senha` | Primeiro acesso | Substituição obrigatória da senha temporária |
| `/` | Autenticado | Dashboard (visão por perfil) |
| `/minhas-ferias` | Autenticado | Histórico de férias do colaborador |
| `/solicitar` | Autenticado | Solicitações de férias e autorização de equipamentos |
| `/minhas-autorizacoes` | Autenticado | Histórico, aceite e termos de equipamentos |
| `/disponibilidade` | Autenticado | Calendário com cores por usuário |
| `/mural` | Autenticado | Mural de avisos internos |
| `/documentos` | Autenticado | Upload e download de documentos |
| `/minhas-credenciais` | Autenticado | Credenciais compartilhadas com o usuário |
| `/aprovacoes` | Admin | Fila de aprovações com histórico |
| `/usuarios` | Admin | Gerenciamento de colaboradores |
| `/patrimonios` | Admin | Inventário, vínculos e manutenção de equipamentos |
| `/departamentos` | Admin | Gerenciamento de departamentos |
| `/bloqueios` | Admin | Bloqueios e recessos de datas |
| `/credenciais` | Admin | Acessos e Senhas (CRUD + permissões) |
| `/relatorios` | Admin | Relatório consolidado |
| `/logs` | Admin | Logs de auditoria com exportação CSV |

---

## Referência da API

Em desenvolvimento, a documentação interativa fica em
**`http://127.0.0.1:8000/docs`** (Swagger) e
**`http://127.0.0.1:8000/redoc`** (ReDoc). Swagger, ReDoc e o schema OpenAPI
são desativados quando `ENVIRONMENT=production`.

### Autenticação

Clientes OAuth2 podem autenticar as rotas protegidas com o header:

```http
Authorization: Bearer <access_token>
```

O token é obtido via `POST /auth/login` e expira após
`ACCESS_TOKEN_EXPIRE_MINUTES` minutos. A aplicação web usa o cookie `HttpOnly`
criado por `POST /auth/session`.

### Endpoints principais

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `POST` | `/auth/session` | — | Login web e criação do cookie de sessão |
| `POST` | `/auth/login` | — | Login OAuth2 com token no corpo |
| `GET` | `/auth/me` | ✓ | Dados do usuário logado |
| `GET` | `/users` | Admin | Listar todos os colaboradores |
| `POST` | `/users` | Admin | Criar colaborador |
| `PUT` | `/users/{id}` | Admin | Editar colaborador |
| `DELETE` | `/users/{id}` | Admin | Remover colaborador |
| `GET` | `/ferias/todas` | Admin | Listar todas as férias |
| `POST` | `/ferias` | ✓ | Solicitar férias |
| `PUT` | `/ferias/{id}/aprovar` | Admin | Aprovar férias |
| `PUT` | `/ferias/{id}/rejeitar` | Admin | Rejeitar férias |
| `GET` | `/ferias/disponibilidade` | ✓ | Calendário de disponibilidade |
| `GET` | `/ferias/feriados/{year}` | ✓ | Feriados nacionais do ano |
| `GET` | `/dashboard` | Admin | Dados do painel administrativo |
| `GET` | `/relatorios` | Admin | Relatório consolidado por colaborador |
| `GET` | `/logs` | Admin | Logs de auditoria paginados |
| `GET` | `/credenciais` | Admin | Listar credenciais |
| `POST` | `/credenciais` | Admin | Criar credencial |
| `PUT` | `/credenciais/{id}/permissoes` | Admin | Atribuir usuários à credencial |
| `GET` | `/credenciais/minhas` | ✓ | Credenciais do usuário logado |
| `GET` | `/bloqueios` | ✓ | Listar bloqueios e recessos |
| `POST` | `/bloqueios` | Admin | Criar bloqueio/recesso |
| `GET` | `/avisos` | ✓ | Listar avisos do mural |
| `POST` | `/avisos` | Admin | Criar aviso |
| `POST` | `/documentos/upload` | ✓ | Upload de documento |
| `GET` | `/documentos/historico` | ✓ | Históricos separados de recebidos e enviados |
| `GET` | `/documentos/{id}/download` | ✓ | Download de documento |
| `GET` | `/patrimonios/me` | ✓ | Equipamentos vinculados ao usuário |
| `GET` | `/patrimonios` | Admin | Inventário paginado e filtros |
| `POST` | `/patrimonios` | Admin | Cadastrar equipamento |
| `POST` | `/autorizacoes-equipamentos` | ✓ | Solicitar equipamentos |
| `GET` | `/autorizacoes-equipamentos/me` | ✓ | Histórico próprio de autorizações |
| `GET` | `/autorizacoes-equipamentos/admin` | Admin | Fila e histórico administrativos |
| `POST` | `/autorizacoes-equipamentos/{id}/aprovar` | Admin | Aprovar integral ou parcialmente |
| `POST` | `/autorizacoes-equipamentos/{id}/entrega` | Admin | Registrar entrega |
| `POST` | `/autorizacoes-equipamentos/{id}/aceite` | Dono | Registrar aceite eletrônico |
| `POST` | `/autorizacoes-equipamentos/{id}/devolucao` | Admin | Registrar devolução |
| `GET` | `/importacao/colaboradores/modelo` | Admin | Baixar modelo Excel para carga de colaboradores |
| `POST` | `/importacao/colaboradores` | Admin | Importar colaboradores via Excel |

---

## Modelos do Banco de Dados

O módulo de patrimônios adiciona equipamentos, vínculos temporais, eventos, solicitações com múltiplos itens e snapshots, versões de termo e eventos de auditoria.

### `users`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String | Nome completo |
| `email` | String UNIQUE | E-mail de acesso |
| `senha_hash` | String | Hash bcrypt da senha |
| `must_change_password` | Boolean | Exige substituição da senha temporária no primeiro acesso |
| `role` | String | `user` ou `admin` |
| `dias_totais` | Integer | Dias creditados em cada concessão anual (padrão: 30) |
| `departamento_id` | FK | Departamento do colaborador |
| `data_admissao` | Date | Data de admissão na empresa |
| `proxima_concessao_ferias` | Date | Próxima data em que a cota anual será creditada |
| `data_aniversario` | Date | Data de aniversário |
| `cor` | String | Cor HEX para identificação visual no calendário |
| `criado_em` | DateTime | Timestamp de criação |

### `ferias`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `user_id` | FK | Colaborador solicitante |
| `data_inicio` | Date | Início do período |
| `data_fim` | Date | Fim do período |
| `dias_usados` | Integer | Calculado: `(fim - início).days + 1` |
| `status` | String | `pendente`, `aprovada`, `rejeitada` |
| `ferias_acordo` | Boolean | Se verdadeiro, não desconta saldo |
| `motivo_rejeicao` | String | Preenchido pelo admin ao rejeitar |
| `aprovado_por_id` | FK | Admin que aprovou |
| `aprovado_em` | DateTime | Timestamp de aprovação |
| `rejeitado_por_id` | FK | Admin que rejeitou |
| `rejeitado_em` | DateTime | Timestamp de rejeição |
| `criado_em` | DateTime | Timestamp da solicitação |

### `saldo_ferias_movimentos`

Registra o saldo inicial de implantação, créditos anuais e ajustes administrativos.
Cada movimento possui quantidade assinada, data de referência, motivo, responsável
e chave idempotente para impedir créditos duplicados.

### `credenciais`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `descricao` | String | Nome do sistema/serviço |
| `email` | String | Login da credencial |
| `senha` | String | Senha criptografada no banco e descriptografada apenas para usuarios autorizados |
| `criado_em` | DateTime | Timestamp de criação |
| `atualizado_em` | DateTime | Última atualização |

### `credencial_usuarios` (N:N)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `credencial_id` | FK (CASCADE) | Credencial |
| `user_id` | FK (CASCADE) | Colaborador com acesso |

### `bloqueios_datas`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `data_inicio` | Date | Início do período bloqueado |
| `data_fim` | Date | Fim do período bloqueado |
| `motivo` | String | Descrição (ex.: "Auditoria externa") |
| `tipo` | String | `bloqueio` ou `recesso` |
| `criado_por_id` | FK | Admin que cadastrou |
| `criado_em` | DateTime | Timestamp de criação |

---

## Regras de Negócio

### Validação de datas para solicitação de férias

Antes de criar uma solicitação, o sistema valida (backend **e** frontend):

1. **Data fim ≥ Data início** — o período deve ser positivo.
2. **Data início ≥ hoje** — férias no passado são bloqueadas.
3. **Não iniciar em fim de semana** (sábado ou domingo).
4. **Regra de feriado na semana:** se há um feriado nacional em uma quinta-feira, os dias anteriores (terça e quarta) também são bloqueados. O sistema consulta o calendário oficial brasileiro via biblioteca `holidays`.
5. **Bloqueios administrativos:** períodos cadastrados pelo admin impedem qualquer solicitação.
6. **Limite simultâneo por departamento:** configurável por departamento (padrão: 2). Validado na criação e na aprovação.

### Saldo de férias

```text
dias_restantes =
  Σ(movimentações de saldo)
  − Σ(dias de férias aprovadas ou pendentes após a implantação)
```

No cadastro, o administrador informa o saldo real disponível na implantação.
A data de admissão não gera créditos retroativos. Ela pode sugerir a próxima
concessão; a data efetiva fica registrada em `proxima_concessao_ferias`. Quando
essa data chega, o sistema credita `dias_totais` uma única vez e avança a próxima
concessão em um ano. Ajustes manuais exigem motivo e geram auditoria.

Férias marcadas como **"por acordo"** (`ferias_acordo = true`) não descontam o saldo.

### Fluxo de aprovação

```
Colaborador cria  →  status: "pendente"
Admin aprova      →  status: "aprovada"  (registra aprovado_por_id + aprovado_em)
Admin rejeita     →  status: "rejeitada" (registra rejeitado_por_id + rejeitado_em + motivo)
Admin cria        →  status: "aprovada"  (bypass direto)
```

### Alertas de contabilidade

Gerados de forma idempotente no login administrativo. As consultas `GET` apenas
leem os alertas persistidos e não alteram o banco. Há lembretes para os marcos
operacionais configurados, sem duplicidade por período de férias e tipo.

---

## Solução de Problemas

### O frontend não conecta na API

Confirme que existe `frontend/.env` com o valor correto:
```env
VITE_API_URL=http://127.0.0.1:8000
```
Em produção com Docker, use `VITE_API_URL=/api`; o Nginx encaminha as requisições internamente ao backend.

### Erro de CORS

O backend aceita apenas a origem configurada em `FRONTEND_URL`. Se ocorrer erro de CORS, confira se `FRONTEND_URL` aponta para a URL usada no navegador e se `VITE_API_URL` aponta para a API sem barra final.

### Container `ferias-backend` reinicia em loop

O backend depende do banco estar saudável. Veja os logs do banco:
```bash
docker compose logs db
```
Se o banco ainda está inicializando, aguarde alguns segundos e verifique novamente com `docker compose ps`.

### Porta já em uso

```bash
# Verificar qual processo usa a porta 8000
sudo lsof -i :8000

# Usar porta alternativa no docker-compose ou no .env:
BACKEND_PORT=8001
FRONTEND_PORT=8080
```

### Backup e restauração do banco

```bash
# Backup
.\scripts\backup.ps1

# Restaurar com backend pausado e migrations ao final
.\scripts\restore.ps1 -BackupFile .\backups\ferias-AAAAMMDD-HHMMSS.zip
```

O pacote `.zip` contém o dump PostgreSQL, os uploads e um manifesto. O arquivo
`.sha256` ao lado do pacote é validado antes da restauração. Por padrão, a
restauração também cria um backup de segurança do estado atual.

### Exportação de Logs

Na tela **Logs do Sistema**, o botão **Exportar CSV** gera o arquivo:
```
logs-gestao-rh-AAAA-MM-DD.csv
```
Formato: separador `;`, BOM UTF-8 (compatível com Excel em PT-BR).  
Colunas: `Data | Ação | Usuário | Detalhes`

---

*Desenvolvido para uso interno do ONRTDPJ — Operador Nacional de Registro de Títulos e Documentos e Pessoas Jurídicas.*
