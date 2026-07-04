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
- Banco de dados PostgreSQL com criação automática de tabelas no startup
- Containerização completa via Docker e Docker Compose
- API RESTful documentada via Swagger (FastAPI)

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
| **Minhas Credenciais** | Visualização das credenciais de sistemas compartilhados que o colaborador tem acesso, com opção de copiar e mostrar/ocultar senhas |

Os documentos sao armazenados em pasta persistente configurada por `UPLOAD_DIR`. Envios feitos por administradores geram uma copia em `enviados/nome-admin/nome-destinatario/arquivo` e outra em `recebidos/nome-destinatario/arquivo`; envios feitos pelo proprio colaborador ficam apenas em `recebidos/nome-colaborador/arquivo`.

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

---

## Tecnologias

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Backend** | Python + FastAPI | 3.12 / 0.110+ |
| **ORM** | SQLAlchemy | 2.x |
| **Banco de Dados** | PostgreSQL | 16 |
| **Autenticação** | JWT via `python-jose` + hash `bcrypt` | — |
| **Feriados** | `holidays` (calendário oficial brasileiro) | — |
| **Frontend** | React + Vite | 18 / 5 |
| **Roteamento** | React Router | 6 |
| **Estilo** | CSS puro com design system de variáveis | — |
| **HTTP Client** | Fetch API nativa | — |
| **Servidor Web** | Nginx (produção) | 1.27-alpine |
| **Containerização** | Docker + Docker Compose | — |

---

## Estrutura do Projeto

```
feriasonr/
├── docker-compose.yml          # Orquestração: db + backend + frontend
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Entrypoint FastAPI, CORS, startup
│       ├── database.py         # Conexão PostgreSQL via SQLAlchemy
│       ├── core/
│       │   └── security.py     # JWT (criar/verificar token), hash bcrypt, guards
│       ├── models/
│       │   ├── user.py         # Tabela users
│       │   ├── ferias.py       # Tabela ferias
│       │   ├── departamento.py # Tabela departamentos
│       │   ├── aviso.py        # Tabela avisos (mural)
│       │   ├── documento.py    # Tabela documentos
│       │   ├── bloqueio.py     # Tabela bloqueios_datas
│       │   ├── alerta.py       # Tabela alertas
│       │   ├── credencial.py   # Tabela credenciais
│       │   └── credencial_usuario.py  # Tabela associativa N:N
│       ├── routers/
│       │   ├── auth.py         # POST /auth/login, GET /auth/me
│       │   ├── users.py        # CRUD /users
│       │   ├── ferias.py       # CRUD /ferias + aprovação + feriados
│       │   ├── relatorios.py   # GET /relatorios, /dashboard, /logs
│       │   ├── departamentos.py
│       │   ├── avisos.py
│       │   ├── documentos.py
│       │   ├── bloqueios.py
│       │   ├── alertas.py
│       │   ├── credenciais.py  # CRUD /credenciais + /minhas + permissões
│       │   └── importacao.py   # POST /importacao (Excel)
│       └── schemas/            # Modelos Pydantic de validação
│
├── frontend/
│   ├── Dockerfile              # Build multistage Node→Nginx
│   ├── nginx.conf              # SPA fallback + cache de assets
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx             # Definição de rotas
│       ├── index.css           # Design system global (variáveis, glass effects)
│       ├── api.js              # Todos os métodos HTTP centralizados
│       ├── context/
│       │   └── AuthContext.jsx # Estado global de autenticação (JWT)
│       ├── components/
│       │   ├── Layout.jsx      # Sidebar + topbar + menu adaptativo por role
│       │   └── PrivateRoute.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Dashboard.jsx
│           ├── MinhasFerias.jsx
│           ├── SolicitarFerias.jsx
│           ├── Disponibilidade.jsx
│           ├── Mural.jsx
│           ├── Documentos.jsx
│           ├── Aprovacoes.jsx
│           ├── Usuarios.jsx
│           ├── Departamentos.jsx
│           ├── Bloqueios.jsx
│           ├── Credenciais.jsx      # Admin: CRUD de credenciais + permissões
│           ├── MinhasCredenciais.jsx # Colaborador: visualizar + copiar senhas
│           ├── Relatorios.jsx
│           ├── Logs.jsx
│           └── _helpers.jsx
│
└── docs/
    ├── API.md
    ├── GUIA-USUARIO.md
    └── DOCKER-SERVIDOR.md
```

---

## Rodando em Desenvolvimento (sem Docker)

### Pré-requisitos

- **Python 3.10+** com `pip`
- **Node.js 18+** com `npm`
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

# Iniciar servidor
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> **O banco é configurado automaticamente** na primeira inicialização: todas as tabelas são criadas via `Base.metadata.create_all()` e o usuário administrador padrão é inserido se não existir.

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

## Deploy em Servidor com Docker

Esta é a forma recomendada para ambientes de produção ou staging. O `docker-compose.yml` orquestra três serviços: **banco de dados (PostgreSQL)**, **backend (FastAPI)** e **frontend (React + Nginx)**.

### Pré-requisitos no servidor

- Docker Engine 24+
- Docker Compose v2 (`docker compose` — sem hífen)
- Pelo menos **1 GB de RAM** disponível
- Portas **80** e **8000** liberadas no firewall

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
SECRET_KEY=cole-aqui-uma-chave-de-64-caracteres-ou-mais-gerada-aleatoriamente
ACCESS_TOKEN_EXPIRE_MINUTES=480
BACKEND_PORT=8000
UPLOAD_DIR=/app/uploads

# ── Frontend ───────────────────────────────────
# Troque pelo IP ou domínio público do servidor
VITE_API_URL=http://SEU_IP_OU_DOMINIO:8000
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

Aguarde o processo concluir (~2-3 minutos na primeira vez). O Docker irá:
1. Baixar as imagens base (`postgres:16-alpine`, `python:3.12-slim`, `node:20-alpine`, `nginx:1.27-alpine`)
2. Instalar as dependências Python e Node
3. Fazer o build de produção do React
4. Copiar os arquivos estáticos para o Nginx
5. Iniciar os três serviços em sequência (o backend aguarda o Postgres estar saudável)

#### 4. Verificar o status dos serviços

```bash
# Ver status dos containers
docker compose ps

# Saída esperada:
# NAME              STATUS          PORTS
# ferias-db         Up (healthy)    5432/tcp
# ferias-backend    Up              0.0.0.0:8000->8000/tcp
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
| **API** (Swagger docs) | `http://SEU_IP_OU_DOMINIO:8000/docs` |
| **Health check** | `http://SEU_IP_OU_DOMINIO:8000/` |

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

# Backup do banco de dados
docker compose exec -T db pg_dump -U ferias ferias > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20240101.sql | docker compose exec -T db psql -U ferias -d ferias
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
    listen 443 ssl;
    server_name seudominio.com.br;

    ssl_certificate     /etc/letsencrypt/live/seudominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com.br/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
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
| `SECRET_KEY` | Chave de assinatura JWT (**trocar em produção!**) | `troque-esta-chave-em-producao` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração da sessão em minutos | `480` (8h) |
| `VITE_API_URL` | URL pública da API (usada no build do React) | `http://chat-server:8000` |
| `FRONTEND_URL` | URL do frontend (CORS) | `http://chat-server` |
| `BACKEND_PORT` | Porta exposta do backend | `8000` |
| `FRONTEND_PORT` | Porta exposta do frontend | `80` |
| `UPLOAD_DIR` | Pasta interna onde documentos enviados sao salvos | `/app/uploads` |

### Backend — `backend/.env` (desenvolvimento local)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave JWT | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração da sessão | `480` |
| `DATABASE_URL` | URL completa do PostgreSQL | `postgresql://ferias:ferias@localhost:5432/ferias` |
| `UPLOAD_DIR` | Pasta local para salvar documentos enviados | `./data/uploads` |

### Frontend — `frontend/.env` (desenvolvimento local)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `VITE_API_URL` | URL base da API | `http://chat-server:8000` |

---

## Credenciais Iniciais

O administrador inicial pode ser criado automaticamente se as variáveis ADMIN_EMAIL e ADMIN_PASSWORD forem configuradas antes da primeira inicialização.

| Campo | Valor |
|-------|-------|
| E-mail | `admin@sistema.com` |
| Senha | `admin123` |
| Perfil | Administrador |

> Recomendamos alterar a senha e o e-mail após o primeiro acesso em produção.

---

## Rotas do Frontend

| Rota | Acesso | Descrição |
|------|--------|-----------|
| `/login` | Público | Tela de autenticação |
| `/` | Autenticado | Dashboard (visão por perfil) |
| `/minhas-ferias` | Autenticado | Histórico de férias do colaborador |
| `/solicitar` | Autenticado | Nova solicitação de férias |
| `/disponibilidade` | Autenticado | Calendário com cores por usuário |
| `/mural` | Autenticado | Mural de avisos internos |
| `/documentos` | Autenticado | Upload e download de documentos |
| `/minhas-credenciais` | Autenticado | Credenciais compartilhadas com o usuário |
| `/aprovacoes` | Admin | Fila de aprovações com histórico |
| `/usuarios` | Admin | Gerenciamento de colaboradores |
| `/departamentos` | Admin | Gerenciamento de departamentos |
| `/bloqueios` | Admin | Bloqueios e recessos de datas |
| `/credenciais` | Admin | Acessos e Senhas (CRUD + permissões) |
| `/relatorios` | Admin | Relatório consolidado |
| `/logs` | Admin | Logs de auditoria com exportação CSV |

---

## Referência da API

A documentação completa e interativa está disponível em:  
**`http://SEU_SERVIDOR:8000/docs`** (Swagger UI)  
**`http://SEU_SERVIDOR:8000/redoc`** (ReDoc)

### Autenticação

Todas as rotas protegidas exigem o header:

```http
Authorization: Bearer <access_token>
```

O token é obtido via `POST /auth/login` e expira após `ACCESS_TOKEN_EXPIRE_MINUTES` minutos.

### Endpoints principais

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `POST` | `/auth/login` | — | Login (form: username + password) |
| `GET` | `/auth/me` | ✓ | Dados do usuário logado |
| `GET` | `/users` | Admin | Listar todos os colaboradores |
| `POST` | `/users` | Admin | Criar colaborador |
| `PUT` | `/users/{id}` | Admin | Editar colaborador |
| `DELETE` | `/users/{id}` | Admin | Remover colaborador |
| `GET` | `/ferias` | Admin | Listar todas as férias |
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
| `GET` | `/documentos/{id}/download` | ✓ | Download de documento |
| `POST` | `/importacao` | Admin | Importar colaboradores via Excel |

---

## Modelos do Banco de Dados

### `users`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String | Nome completo |
| `email` | String UNIQUE | E-mail de acesso |
| `senha_hash` | String | Hash bcrypt da senha |
| `role` | String | `user` ou `admin` |
| `dias_totais` | Integer | Saldo total de férias (padrão: 30) |
| `departamento_id` | FK | Departamento do colaborador |
| `data_admissao` | Date | Data de admissão na empresa |
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

### `credenciais`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `descricao` | String | Nome do sistema/serviço |
| `email` | String | Login da credencial |
| `senha` | String | Senha (armazenada em texto — protegida por perfil) |
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

```
dias_restantes = dias_totais − Σ(dias_usados de férias aprovadas ou pendentes no ciclo atual)
```

O ciclo é baseado no aniversário de empresa do colaborador (data de admissão).

Férias marcadas como **"por acordo"** (`ferias_acordo = true`) não descontam o saldo.

### Fluxo de aprovação

```
Colaborador cria  →  status: "pendente"
Admin aprova      →  status: "aprovada"  (registra aprovado_por_id + aprovado_em)
Admin rejeita     →  status: "rejeitada" (registra rejeitado_por_id + rejeitado_em + motivo)
Admin cria        →  status: "aprovada"  (bypass direto)
```

### Alertas de contabilidade

Gerados automaticamente ao acessar `/alertas`. Disparados para cada férias aprovada com início **exatamente em 4 dias**. Sem duplicidade: um alerta por período de férias.

---

## Solução de Problemas

### O frontend não conecta na API

Confirme que existe `frontend/.env` com o valor correto:
```env
VITE_API_URL=http://127.0.0.1:8000
```
Em produção com Docker, confirme que `VITE_API_URL` no `.env` raiz aponta para o IP/domínio acessível publicamente.

### Erro de CORS

O backend aceita qualquer origem em modo padrão (`allow_origins=["*"]`). Se ocorrer erro de CORS mesmo assim, verifique se o `VITE_API_URL` não tem barra no final e se o backend iniciou sem erros.

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
docker compose exec -T db pg_dump -U ferias ferias > backup_$(date +%Y%m%d_%H%M).sql

# Restaurar em container novo
docker compose exec -T db psql -U ferias -d ferias < backup_20240101_1200.sql
```

### Exportação de Logs

Na tela **Logs do Sistema**, o botão **Exportar CSV** gera o arquivo:
```
logs-gestao-rh-AAAA-MM-DD.csv
```
Formato: separador `;`, BOM UTF-8 (compatível com Excel em PT-BR).  
Colunas: `Data | Ação | Usuário | Detalhes`

---

## Documentação Complementar

- [Referência completa da API](docs/API.md)
- [Guia do Usuário](docs/GUIA-USUARIO.md)
- [Deploy detalhado em servidor](docs/DOCKER-SERVIDOR.md)

---

*Desenvolvido para uso interno do ONRTDPJ — Operador Nacional de Registro de Títulos e Documentos e Pessoas Jurídicas.*
