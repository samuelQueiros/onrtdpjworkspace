# Sistema de Gestao de Ferias ONRTDPJ

Sistema web para controle de ferias de colaboradores, com login, saldo de dias, solicitacao/cancelamento de periodos, calendario de disponibilidade, administracao de usuarios, relatorios e logs exportaveis para Excel.

## Sumario

- [Visao Geral](#visao-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Regras de Negocio](#regras-de-negocio)
- [Instalacao](#instalacao)
- [Execucao](#execucao)
- [Credenciais Iniciais](#credenciais-iniciais)
- [Frontend](#frontend)
- [Backend](#backend)
- [Banco de Dados](#banco-de-dados)
- [Seguranca](#seguranca)
- [Exportacao de Logs](#exportacao-de-logs)
- [Deploy](#deploy)
- [Solucao de Problemas](#solucao-de-problemas)
- [Documentos Complementares](#documentos-complementares)

## Visao Geral

O sistema foi criado para centralizar o fluxo de ferias de uma equipe:

1. O colaborador acessa o sistema com email e senha.
2. Consulta seu saldo de dias disponiveis.
3. Solicita um periodo de ferias.
4. O sistema valida saldo e disponibilidade.
5. Todos os usuarios conseguem visualizar ferias marcadas no calendario.
6. Administradores conseguem gerenciar usuarios, consultar relatorios e auditar logs.

## Funcionalidades

### Colaborador

- Login autenticado com token JWT.
- Dashboard com saldo de ferias, dias usados e proximos periodos.
- Consulta de ferias ja registradas.
- Solicitacao de novo periodo.
- Cancelamento de ferias proprias.
- Visualizacao do calendario de disponibilidade.
- Visualizacao das ferias marcadas por todos os colaboradores.

### Administrador

- Todas as funcionalidades de colaborador.
- Cadastro de novos usuarios.
- Edicao de nome, email e dias totais dos usuarios.
- Consulta de relatorio consolidado por colaborador.
- Consulta de logs do sistema.
- Exportacao dos logs em arquivo `.csv` compativel com Excel.

## Tecnologias

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT com `python-jose`
- Hash de senha com `bcrypt`
- Uvicorn

### Frontend

- React 18
- Vite
- React Router
- CSS puro com variaveis de design
- Fetch API

## Estrutura do Projeto

```text
FERIAS ONRTDPJ/
  backend/
    app/
      core/
        security.py
      models/
        user.py
        ferias.py
        log.py
      routers/
        auth.py
        users.py
        ferias.py
        relatorios.py
      schemas/
        user.py
        ferias.py
        log.py
      database.py
      main.py
    .env.example
    ferias.db
    requirements.txt

  frontend/
    src/
      components/
        Layout.jsx
        PrivateRoute.jsx
      context/
        AuthContext.jsx
      pages/
        Dashboard.jsx
        Disponibilidade.jsx
        Login.jsx
        Logs.jsx
        MinhasFerias.jsx
        Relatorios.jsx
        SolicitarFerias.jsx
        Usuarios.jsx
        _helpers.jsx
      api.js
      index.css
      main.jsx
      App.jsx
    index.html
    package.json
    vite.config.js

  docs/
    API.md
    GUIA-USUARIO.md
```

## Regras de Negocio

### Saldo de ferias

- Cada usuario possui um campo `dias_totais`.
- Por padrao, novos usuarios recebem `30` dias.
- O saldo restante e calculado assim:

```text
dias_restantes = dias_totais - soma(dias_usados em ferias registradas)
```

### Contagem de dias

A contagem e inclusiva:

```text
dias_usados = data_fim - data_inicio + 1
```

Exemplo:

- Inicio: `05/05/2026`
- Fim: `19/05/2026`
- Total: `15` dias

### Limite simultaneo

O sistema usa a constante:

```python
LIMITE_SIMULTANEO = 2
```

Isso significa que no maximo 2 colaboradores podem estar em ferias ao mesmo tempo.

Se o periodo solicitado tiver algum dia onde ja existem 2 colaboradores em ferias, a solicitacao e bloqueada.

### Disponibilidade

A rota de disponibilidade retorna:

- `ferias_marcadas`: todos os periodos de ferias cadastrados.
- `periodos_bloqueados`: periodos onde o limite simultaneo foi atingido.

No frontend:

- Azul: ha ferias marcadas naquele dia.
- Vermelho: o limite simultaneo foi atingido naquele dia.

### Permissoes

Usuarios comuns:

- Visualizam suas proprias ferias.
- Criam suas proprias ferias.
- Editam/cancelam apenas suas proprias ferias.
- Visualizam disponibilidade global.

Administradores:

- Acessam usuarios, relatorios e logs.
- Criam e editam usuarios.
- Visualizam todos os relatorios.

## Instalacao

### Pre-requisitos

- Python 3.10 ou superior
- Node.js 18 ou superior
- npm

### Backend

Entre na pasta do backend:

```powershell
cd backend
```

Crie um ambiente virtual:

```powershell
python -m venv venv
```

Ative o ambiente virtual no PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e defina uma chave segura:

```env
SECRET_KEY=troque-por-uma-chave-grande-e-segura
ACCESS_TOKEN_EXPIRE_MINUTES=480
FRONTEND_URL=http://127.0.0.1:5173
```

### Frontend

Entre na pasta do frontend:

```powershell
cd frontend
```

Instale as dependencias:

```powershell
npm install
```

Opcionalmente crie um arquivo `.env` no frontend para trocar a URL da API:

```env
VITE_API_URL=http://chat-server:8000
```

Se esse arquivo nao existir, o frontend usa `http://chat-server:8000`.

## Execucao

### Executar backend

Na pasta `backend`:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API:

```text
http://127.0.0.1:8000
```

Documentacao interativa do FastAPI:

```text
http://127.0.0.1:8000/docs
```

### Executar frontend

Na pasta `frontend`:

```powershell
npm run dev
```

Aplicacao:

```text
http://127.0.0.1:5173
```

### Build de producao

Na pasta `frontend`:

```powershell
npm run build
```

Os arquivos finais ficam em:

```text
frontend/dist/
```

## Credenciais Iniciais

No primeiro start do backend, se nao existir administrador, o sistema cria automaticamente:

```text
Email: admin@sistema.com
Senha: admin123
Perfil: admin
```

Recomendacao: altere essa senha em ambiente real. Atualmente o sistema nao possui tela de troca de senha, entao a troca deve ser feita via ajuste de banco/script ou implementacao futura.

## Frontend

### Rotas

| Rota | Acesso | Descricao |
|---|---|---|
| `/login` | Publico | Tela de login |
| `/` | Autenticado | Dashboard |
| `/minhas-ferias` | Autenticado | Ferias do usuario atual |
| `/solicitar` | Autenticado | Nova solicitacao de ferias |
| `/disponibilidade` | Autenticado | Calendario global de ferias |
| `/usuarios` | Admin | Cadastro e edicao de usuarios |
| `/relatorios` | Admin | Relatorio consolidado |
| `/logs` | Admin | Auditoria e exportacao |

### Arquivos principais

- `frontend/src/App.jsx`: define as rotas.
- `frontend/src/api.js`: concentra chamadas HTTP para o backend.
- `frontend/src/context/AuthContext.jsx`: controla login, usuario atual e logout.
- `frontend/src/components/PrivateRoute.jsx`: protege rotas autenticadas/admin.
- `frontend/src/components/Layout.jsx`: sidebar, topo e menu principal.
- `frontend/src/index.css`: design system e estilos globais.

### Formato de datas

As datas sao exibidas no formato:

```text
DD/MM/AAAA
```

Internamente, inputs HTML e API usam:

```text
AAAA-MM-DD
```

## Backend

### Inicializacao

Arquivo:

```text
backend/app/main.py
```

Responsabilidades:

- Criar app FastAPI.
- Configurar CORS.
- Registrar routers.
- Criar tabelas automaticamente.
- Criar administrador padrao no primeiro start.

### Routers

| Arquivo | Prefixo | Responsabilidade |
|---|---|---|
| `auth.py` | `/auth` | Login e usuario atual |
| `users.py` | `/users`, `/me/configuracoes` | Usuarios e configuracoes |
| `ferias.py` | `/ferias` | Ferias e disponibilidade |
| `relatorios.py` | `/relatorios`, `/logs` | Relatorios e logs |

### Modelos

#### User

Tabela: `users`

| Campo | Tipo | Descricao |
|---|---|---|
| `id` | int | Identificador |
| `nome` | string | Nome do usuario |
| `email` | string | Email unico |
| `senha_hash` | string | Senha criptografada |
| `role` | string | `user` ou `admin` |
| `dias_totais` | int | Total de dias disponiveis |
| `criado_em` | datetime | Data de criacao |

#### Ferias

Tabela: `ferias`

| Campo | Tipo | Descricao |
|---|---|---|
| `id` | int | Identificador |
| `user_id` | int | Usuario dono das ferias |
| `data_inicio` | date | Inicio do periodo |
| `data_fim` | date | Fim do periodo |
| `dias_usados` | int | Dias calculados automaticamente |
| `criado_em` | datetime | Data de criacao |

#### Log

Tabela: `logs`

| Campo | Tipo | Descricao |
|---|---|---|
| `id` | int | Identificador |
| `user_id` | int | Usuario associado |
| `acao` | string | Nome da acao |
| `detalhes` | string | Detalhes da acao |
| `criado_em` | datetime | Data do registro |

## Banco de Dados

O projeto usa SQLite:

```text
backend/ferias.db
```

A string de conexao esta em:

```text
backend/app/database.py
```

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./ferias.db"
```

As tabelas sao criadas automaticamente no startup do backend:

```python
Base.metadata.create_all(bind=engine)
```

## Seguranca

### Autenticacao

O login usa OAuth2 Password Flow:

```text
POST /auth/login
```

O backend retorna um token JWT:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {}
}
```

O frontend guarda o token em:

```text
localStorage.token
```

As requisicoes autenticadas enviam:

```http
Authorization: Bearer <token>
```

### Senhas

As senhas sao armazenadas com hash `bcrypt`.

### Variaveis de ambiente

| Variavel | Descricao | Padrao |
|---|---|---|
| `SECRET_KEY` | Chave para assinar JWT | `chave-secreta-padrao-troque-em-producao` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duracao do token | `480` |
| `FRONTEND_URL` | URL do frontend em producao | Exemplo Lovable |

### Recomendacoes para producao

- Trocar `SECRET_KEY`.
- Restringir CORS em `backend/app/main.py`.
- Usar HTTPS.
- Implementar troca de senha.
- Implementar reset de senha.
- Considerar banco de dados gerenciado para producao.

## Exportacao de Logs

Na tela:

```text
Logs do Sistema
```

O botao `Exportar Excel` gera um arquivo:

```text
logs-ferias-AAAA-MM-DD.csv
```

O arquivo usa:

- Separador `;`, comum no Excel em configuracoes PT-BR.
- BOM UTF-8 para preservar acentuacao.
- Linha `sep=;` para orientar o Excel.

Colunas exportadas:

- Data
- Acao
- Usuario
- Detalhes

## Deploy

### Backend

Para producao, rode FastAPI com Uvicorn/Gunicorn ou servico equivalente:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Configure variaveis de ambiente reais:

```env
SECRET_KEY=chave-real
ACCESS_TOKEN_EXPIRE_MINUTES=480
FRONTEND_URL=https://seu-front-end.com
```

### Frontend

Gere o build:

```powershell
npm run build
```

Publique a pasta:

```text
frontend/dist/
```

Configure a URL da API no build:

```env
VITE_API_URL=https://sua-api.com
```

## Solucao de Problemas

### Erro de CORS

Verifique `backend/app/main.py`.

Durante desenvolvimento, o backend esta com:

```python
allow_origins=["*"]
```

Em producao, substitua por:

```python
allow_origins=["https://seu-front-end.com"]
```

### Frontend nao conecta na API

Confirme se o backend esta rodando:

```text
http://127.0.0.1:8000
```

Confirme `VITE_API_URL` ou o valor padrao em:

```text
frontend/src/api.js
```

### Token expirado

Se o token expirar:

1. O usuario deve sair.
2. Acessar novamente pela tela de login.

### Banco nao cria tabelas

Verifique se o backend iniciou sem erro e se o processo tem permissao de escrita na pasta `backend`.

### Porta ocupada

Backend:

```powershell
uvicorn app.main:app --reload --port 8001
```

Frontend:

```powershell
npm run dev -- --port 5174
```

## Testes e Verificacao

Comandos usados para validar:

```powershell
python -m py_compile backend\app\routers\ferias.py
```

```powershell
cd frontend
npm run build
```

## Melhorias Futuras

- Tela de troca de senha.
- Recuperacao de senha por email.
- Aprovacao/reprovacao de solicitacoes antes de registrar ferias.
- Status de ferias: pendente, aprovada, cancelada.
- Filtro por usuario no calendario.
- Exportacao de relatorios.
- Testes automatizados.
- Migracoes com Alembic.
- Banco PostgreSQL em producao.
- Historico completo de alteracoes de usuario.

## Documentos Complementares

- [API](docs/API.md)
- [Guia do Usuario](docs/GUIA-USUARIO.md)
- [Docker em Servidor](docs/DOCKER-SERVIDOR.md)
