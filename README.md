# Gestão RH — ONRTDPJ

Sistema web completo para gestão de férias e RH de colaboradores. Inclui controle de saldo, solicitação/aprovação de períodos, calendário visual com cores por usuário, dashboard administrativo, bloqueio de datas, alertas de contabilidade e logs completos.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Rodar Localmente](#como-rodar-localmente)
- [Credenciais Iniciais](#credenciais-iniciais)
- [Rotas do Frontend](#rotas-do-frontend)
- [Routers da API](#routers-da-api)
- [Modelos do Banco](#modelos-do-banco)
- [Regras de Negócio](#regras-de-negócio)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy com Docker](#deploy-com-docker)
- [Solução de Problemas](#solução-de-problemas)

---

## Funcionalidades

### Colaborador

- Login com JWT.
- Dashboard pessoal: saldo de dias, dias usados, próximas férias.
- Solicitação de férias (com validação de saldo e disponibilidade).
- Férias por acordo (não descontam saldo).
- Edição e cancelamento de férias próprias.
- Calendário de disponibilidade com cores por usuário.
- Visualização de bloqueios e recessos cadastrados pelo admin.
- Mural de avisos.
- Upload e download de documentos.

### Administrador

- Todas as funcionalidades de colaborador.
- **Dashboard administrativo**: total de colaboradores, férias aprovadas/pendentes/rejeitadas, pessoas em férias hoje, próximas férias 30 dias, alertas de contabilidade.
- **Aprovação de férias** com filtros (Pendente / Aprovada / Rejeitada / Todas) e histórico completo (quem aprovou/rejeitou e quando).
- **Cor por usuário**: cada colaborador tem uma cor HEX para identificação visual no calendário e no dashboard.
- **Bloqueio de datas**: impede solicitações em períodos críticos (auditorias, fechamentos).
- **Recesso coletivo**: cadastro de período de recesso visível no calendário.
- **Alertas de contabilidade**: notificação automática 4 dias antes do início de cada férias aprovada.
- Cadastro/edição de usuários com cor, departamento, data de admissão e aniversário.
- Gerenciamento de departamentos com limite simultâneo configurável.
- Relatórios consolidados por colaborador.
- Logs completos de auditoria com exportação CSV.
- Mural de avisos (criar, fixar, expirar).

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite, Uvicorn |
| Auth | JWT via `python-jose`, hash `bcrypt` |
| Frontend | React 18, Vite, React Router 6 |
| Estilo | CSS puro com variáveis de design (sem framework) |
| Deploy | Docker + Docker Compose (opcional) |

---

## Estrutura do Projeto

```
feriasonr/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── security.py          # JWT, hash, dependências de auth
│   │   ├── models/
│   │   │   ├── user.py              # Usuário (+ campo cor)
│   │   │   ├── ferias.py            # Férias (+ histórico aprovação)
│   │   │   ├── log.py               # Logs de auditoria
│   │   │   ├── departamento.py      # Departamentos
│   │   │   ├── aviso.py             # Mural de avisos
│   │   │   ├── documento.py         # Documentos
│   │   │   ├── bloqueio.py          # Bloqueios/recessos de datas
│   │   │   └── alerta.py            # Alertas de contabilidade
│   │   ├── routers/
│   │   │   ├── auth.py              # Login e /auth/me
│   │   │   ├── users.py             # CRUD de usuários
│   │   │   ├── ferias.py            # Férias, aprovação, disponibilidade
│   │   │   ├── relatorios.py        # Relatórios, /dashboard, /logs
│   │   │   ├── departamentos.py     # CRUD de departamentos
│   │   │   ├── avisos.py            # CRUD do mural
│   │   │   ├── documentos.py        # Upload/download de documentos
│   │   │   ├── bloqueios.py         # CRUD de bloqueios/recessos
│   │   │   ├── alertas.py           # Alertas de contabilidade
│   │   │   └── importacao.py        # Importação via Excel
│   │   ├── schemas/                 # Schemas Pydantic
│   │   ├── database.py              # Conexão SQLite
│   │   └── main.py                  # App FastAPI, migrations, startup
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx           # Sidebar, topbar, menu
│   │   │   └── PrivateRoute.jsx     # Guarda de rotas
│   │   ├── context/
│   │   │   └── AuthContext.jsx      # Estado global de autenticação
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx        # Dashboard (usuário e admin)
│   │   │   ├── Aprovacoes.jsx       # Aprovação com filtros e histórico
│   │   │   ├── Disponibilidade.jsx  # Calendário com cores
│   │   │   ├── Usuarios.jsx         # CRUD com color picker
│   │   │   ├── Bloqueios.jsx        # Bloqueios e recessos
│   │   │   ├── MinhasFerias.jsx
│   │   │   ├── SolicitarFerias.jsx
│   │   │   ├── Departamentos.jsx
│   │   │   ├── Mural.jsx
│   │   │   ├── Documentos.jsx
│   │   │   ├── Relatorios.jsx
│   │   │   ├── Logs.jsx
│   │   │   ├── Login.jsx
│   │   │   └── _helpers.jsx         # Componentes compartilhados
│   │   ├── api.js                   # Todas as chamadas HTTP
│   │   ├── index.css                # Design system global
│   │   ├── App.jsx                  # Rotas
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── API.md
│   ├── GUIA-USUARIO.md
│   └── DOCKER-SERVIDOR.md
└── docker-compose.yml
```

---

## Como Rodar Localmente

### Pré-requisitos

- **Python 3.10+**
- **Node.js 18+** e **npm**
- Terminal (bash, zsh, PowerShell ou cmd)

---

### 1. Clonar / entrar na pasta

```bash
cd feriasonr
```

---

### 2. Backend

#### Criar e ativar ambiente virtual

**Linux / macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (cmd):**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

#### Instalar dependências

```bash
pip install -r requirements.txt
```

#### Criar arquivo `.env`

**Linux / macOS:**
```bash
cp .env.example .env
```

**Windows:**
```powershell
Copy-Item .env.example .env
```

Edite o `.env`:

```env
SECRET_KEY=troque-por-uma-chave-longa-e-aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=480
DATABASE_PATH=./ferias.db
```

#### Iniciar o servidor

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O backend estará em: **http://127.0.0.1:8000**

Documentação interativa (Swagger): **http://127.0.0.1:8000/docs**

> Na primeira inicialização, o banco de dados é criado automaticamente e o administrador padrão é gerado.

---

### 3. Frontend

Em outro terminal:

```bash
cd frontend
npm install
```

Crie um arquivo `.env` na pasta `frontend`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

> **Importante:** sem esse arquivo o frontend tenta conectar em `http://chat-server:8000` (endereço do servidor Docker). Para rodar local, o `.env` é obrigatório.

Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

A aplicação estará em: **http://127.0.0.1:5173**

---

### 4. Resumo dos comandos (todos de uma vez)

Abra **dois terminais** e rode em paralelo:

**Terminal 1 — Backend:**
```bash
cd feriasonr/backend
python3 -m venv venv && source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# edite o .env conforme necessário
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd feriasonr/frontend
npm install
echo "VITE_API_URL=http://127.0.0.1:8000" > .env
npm run dev
```

Acesse: **http://127.0.0.1:5173**

---

## Credenciais Iniciais

Geradas automaticamente no primeiro start:

| Campo | Valor |
|-------|-------|
| E-mail | `admin@sistema.com` |
| Senha | `admin123` |
| Perfil | Administrador |

> Altere a senha após o primeiro acesso via painel de configurações.

---

## Rotas do Frontend

| Rota | Acesso | Descrição |
|------|--------|-----------|
| `/login` | Público | Tela de login |
| `/` | Autenticado | Dashboard (resumo pessoal ou painel admin) |
| `/minhas-ferias` | Autenticado | Histórico de férias do usuário |
| `/solicitar` | Autenticado | Nova solicitação de férias |
| `/disponibilidade` | Autenticado | Calendário com cores por usuário |
| `/mural` | Autenticado | Mural de avisos |
| `/documentos` | Autenticado | Upload e download de documentos |
| `/aprovacoes` | Admin | Aprovação com filtros e histórico |
| `/usuarios` | Admin | CRUD de colaboradores + color picker |
| `/departamentos` | Admin | CRUD de departamentos |
| `/bloqueios` | Admin | Bloqueios de datas e recessos |
| `/relatorios` | Admin | Relatório consolidado |
| `/logs` | Admin | Logs de auditoria |

---

## Routers da API

| Arquivo | Prefixo / Rotas | Descrição |
|---------|----------------|-----------|
| `auth.py` | `POST /auth/login`, `GET /auth/me` | Autenticação JWT |
| `users.py` | `/users`, `/me/configuracoes` | Usuários |
| `ferias.py` | `/ferias` | Férias, aprovação, disponibilidade |
| `relatorios.py` | `/relatorios`, `/dashboard`, `/logs` | Relatórios e dashboard admin |
| `departamentos.py` | `/departamentos` | Departamentos |
| `avisos.py` | `/avisos` | Mural |
| `documentos.py` | `/documentos` | Documentos |
| `bloqueios.py` | `/bloqueios` | Bloqueios e recessos |
| `alertas.py` | `/alertas` | Alertas de contabilidade |
| `importacao.py` | `/importacao` | Importação Excel |

---

## Modelos do Banco

### `users`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | PK |
| `nome` | string | Nome completo |
| `email` | string | E-mail único |
| `senha_hash` | string | Senha bcrypt |
| `role` | string | `user` ou `admin` |
| `dias_totais` | int | Saldo total de dias |
| `departamento_id` | int (FK) | Departamento |
| `data_admissao` | date | Data de admissão |
| `data_aniversario` | date | Aniversário |
| `cor` | string | Cor HEX para identificação visual |
| `criado_em` | datetime | Data de criação |

### `ferias`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | PK |
| `user_id` | int (FK) | Dono das férias |
| `data_inicio` | date | Início do período |
| `data_fim` | date | Fim do período |
| `dias_usados` | int | Calculado automaticamente |
| `status` | string | `pendente`, `aprovada`, `rejeitada` |
| `ferias_acordo` | bool | Não desconta saldo |
| `motivo_rejeicao` | string | Preenchido ao rejeitar |
| `aprovado_por_id` | int (FK) | Admin que aprovou |
| `aprovado_em` | datetime | Quando foi aprovado |
| `rejeitado_por_id` | int (FK) | Admin que rejeitou |
| `rejeitado_em` | datetime | Quando foi rejeitado |
| `criado_em` | datetime | Data da solicitação |

### `bloqueios_datas`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | PK |
| `data_inicio` | date | Início do bloqueio |
| `data_fim` | date | Fim do bloqueio |
| `motivo` | string | Descrição (ex.: "Auditoria") |
| `tipo` | string | `bloqueio` ou `recesso` |
| `criado_por_id` | int (FK) | Admin que criou |
| `criado_em` | datetime | Data de criação |

### `alertas`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | PK |
| `ferias_id` | int (FK) | Férias associadas |
| `tipo` | string | `contabilidade_4dias` |
| `mensagem` | string | Texto do alerta |
| `lido` | bool | Lido pelo admin |
| `criado_em` | datetime | Data de geração |

---

## Regras de Negócio

### Saldo de férias

```
dias_restantes = dias_totais - soma(dias_usados das férias aprovadas/pendentes no ciclo)
```

O ciclo é baseado na data de admissão do colaborador (aniversário de empresa).

### Contagem de dias (inclusiva)

```
dias_usados = data_fim - data_inicio + 1
```

### Férias por acordo

- Marcadas com `ferias_acordo = true`.
- **Não** descontam saldo do colaborador.
- Identificadas visualmente com badge "Por acordo".
- Ainda passam pelo fluxo de aprovação quando criadas por usuário comum.

### Fluxo de aprovação

- Usuário comum cria férias com status `pendente`.
- Admin cria férias direto como `aprovada`.
- Admin pode aprovar (`pendente → aprovada`) ou rejeitar (`pendente → rejeitada`).
- Histórico salvo: quem aprovou/rejeitou e data/hora exata.

### Limite simultâneo por departamento

- Configurado em cada departamento (campo `limite_simultaneo`).
- Fallback global: 2 colaboradores simultâneos.
- Validado tanto na criação quanto na aprovação.

### Bloqueio de datas

- Admin cadastra períodos com tipo `bloqueio` ou `recesso`.
- Nenhum colaborador pode solicitar férias nesse intervalo (validação no backend e no frontend).
- Mensagem amigável exibida ao tentar.

### Alertas de contabilidade

- Gerados automaticamente ao acessar `/alertas`.
- Disparados para cada férias aprovada que começa em exatamente 4 dias.
- Sem duplicidade: um alerta por férias.
- Visíveis no dashboard admin.

---

## Variáveis de Ambiente

### Backend — `backend/.env`

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave de assinatura JWT | `chave-secreta-padrao-troque-em-producao` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração do token (minutos) | `480` |
| `DATABASE_PATH` | Caminho do arquivo SQLite | `./ferias.db` |

### Frontend — `frontend/.env`

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `VITE_API_URL` | URL base da API | `http://chat-server:8000` |

---

## Deploy com Docker

O projeto possui `docker-compose.yml` pronto.

```bash
# Na raiz do projeto (pasta feriasonr)
docker compose up --build
```

Para configurar variáveis de ambiente no Docker, copie o exemplo:

```bash
cp .env.docker.example .env.docker
```

Edite `.env.docker` com suas configurações e consulte o guia completo em:

```
docs/DOCKER-SERVIDOR.md
```

---

## Build de Produção (sem Docker)

```bash
cd frontend
npm run build
```

Os arquivos estáticos ficam em `frontend/dist/` e podem ser servidos por qualquer servidor web (Nginx, Apache, Caddy).

---

## Solução de Problemas

### Frontend não conecta na API

Verifique se existe `frontend/.env` com:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Confirme que o backend está rodando na mesma porta.

### Erro de CORS

Em desenvolvimento o backend aceita qualquer origem (`allow_origins=["*"]`). Se encontrar erro de CORS, confirme que o `VITE_API_URL` está correto e que o backend subiu sem erros.

### Banco não cria tabelas

O banco é criado automaticamente no startup. Verifique se o processo tem permissão de escrita na pasta `backend/` e se não há erro no terminal do backend.

### Porta ocupada

```bash
# Backend em porta alternativa
uvicorn app.main:app --reload --port 8001

# Frontend em porta alternativa
npm run dev -- --port 5174
```

Lembre de atualizar `VITE_API_URL` no `.env` do frontend caso troque a porta do backend.

### Migrations automáticas

O sistema roda migrations leves no startup (`ALTER TABLE ... ADD COLUMN`). Colunas já existentes são ignoradas sem erro. Se precisar resetar o banco, basta excluir `backend/ferias.db` e reiniciar o backend.

---

## Exportação de Logs

Na tela **Logs do Sistema**, o botão **Exportar CSV** gera:

```
logs-gestao-rh-AAAA-MM-DD.csv
```

- Separador `;` (padrão PT-BR para Excel).
- BOM UTF-8 para acentuação correta.
- Colunas: Data, Ação, Usuário, Detalhes.

---

## Documentos Complementares

- [API — Referência de endpoints](docs/API.md)
- [Guia do Usuário](docs/GUIA-USUARIO.md)
- [Deploy em Servidor com Docker](docs/DOCKER-SERVIDOR.md)
