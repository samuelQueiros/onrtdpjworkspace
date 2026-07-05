# Guia de Docker em Servidor

Este guia explica como publicar o Sistema de Gestao de Ferias ONRTDPJ em um servidor usando Docker e Docker Compose.

## Visao Geral

O Docker Compose sobe tres servicos:

| Servico | Container | Porta | Funcao |
|---|---|---|---|
| `db` | `ferias-db` | interna `5432` | Banco PostgreSQL |
| `backend` | `ferias-backend` | `8000` | API FastAPI |
| `frontend` | `ferias-frontend` | `80` | Interface React servida por Nginx |

O banco PostgreSQL fica em volume Docker, e os documentos enviados ficam em uma pasta do servidor montada no container:

```text
ferias_data:/var/lib/postgresql/data
./uploads:/app/uploads
```

Isso evita perder o banco ao recriar containers e deixa os arquivos acessiveis diretamente na maquina em `uploads/`. A porta do PostgreSQL nao e publicada no host por padrao; o backend acessa o banco pela rede interna do Docker usando o hostname `db`.

Os documentos sao organizados dentro da pasta `uploads/` por envio administrativo e recebimento:

```text
uploads/enviados/nome-admin/nome-destinatario/arquivo
uploads/recebidos/nome-destinatario/arquivo
```

Quando um colaborador envia seu proprio documento, o arquivo fica apenas em `uploads/recebidos/nome-colaborador/arquivo`.

## Arquivos Docker

Na raiz do projeto:

```text
docker-compose.yml
.env.docker.example
```

No backend:

```text
backend/Dockerfile
backend/.dockerignore
```

No frontend:

```text
frontend/Dockerfile
frontend/nginx.conf
frontend/.dockerignore
```

## Instalar Docker no Servidor

Em Ubuntu/Debian:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
```

Adicione a chave oficial:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Adicione o repositorio:

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Instale:

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verifique:

```bash
docker --version
docker compose version
```

Opcional, para usar Docker sem `sudo`:

```bash
sudo usermod -aG docker $USER
```

Depois faca logout/login no servidor.

## Enviar Projeto para o Servidor

Exemplo com `scp`:

```bash
scp -r "FERIAS ONRTDPJ" usuario@IP_DO_SERVIDOR:/opt/ferias-onrtdpj
```

Entre na pasta:

```bash
cd /opt/ferias-onrtdpj
```

Crie a pasta de documentos no servidor:

```bash
mkdir -p uploads
chown -R 1000:1000 uploads
chmod 775 uploads
```

O backend roda como usuario nao-root no container usando UID/GID `1000`. Por isso a pasta `uploads/` precisa permitir escrita para esse usuario.

## Configurar `.env`

Copie o exemplo:

```bash
cp .env.docker.example .env
```

Edite:

```bash
nano .env
```

Exemplo usando IP:

```env
ENVIRONMENT=production
SECRET_KEY=troque-por-uma-chave-longa-e-segura
CREDENTIALS_ENCRYPTION_KEY=troque-por-outra-chave-longa-e-segura-para-credenciais
ACCESS_TOKEN_EXPIRE_MINUTES=480

FRONTEND_URL=http://123.123.123.123
VITE_API_URL=http://123.123.123.123:8000

FRONTEND_PORT=80
BACKEND_PORT=8000
UPLOAD_DIR=/app/uploads

ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=troque-por-uma-senha-forte
```

Exemplo usando dominio:

```env
ENVIRONMENT=production
SECRET_KEY=troque-por-uma-chave-longa-e-segura
CREDENTIALS_ENCRYPTION_KEY=troque-por-outra-chave-longa-e-segura-para-credenciais
ACCESS_TOKEN_EXPIRE_MINUTES=480

FRONTEND_URL=https://ferias.seudominio.com
VITE_API_URL=https://api-ferias.seudominio.com

FRONTEND_PORT=80
BACKEND_PORT=8000
UPLOAD_DIR=/app/uploads

ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=troque-por-uma-senha-forte
```

Importante:

- `VITE_API_URL` precisa ser acessivel pelo navegador dos usuarios.
- Nao use `chat-server` em producao, a menos que o sistema seja acessado apenas na propria maquina.
- Se alterar `VITE_API_URL`, e necessario rebuildar o frontend.
- `UPLOAD_DIR` deve apontar para a pasta interna usada pelo container, normalmente `/app/uploads`.
- No servidor, os arquivos ficam disponiveis na pasta `uploads/` da raiz do projeto.
- O PostgreSQL fica acessivel apenas para os containers da aplicacao. Para acessar o banco manualmente, use `docker compose exec db psql -U ferias -d ferias`.

## Subir o Sistema

Na raiz do projeto:

```bash
docker compose up -d --build
```

Ao iniciar o backend, o container executa automaticamente:

```bash
alembic upgrade head
```

Isso aplica as migrations do banco antes de iniciar a API FastAPI.

Verifique:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs -f
```

## Acessar

Frontend:

```text
http://IP_DO_SERVIDOR
```

Backend:

```text
http://IP_DO_SERVIDOR:8000
```

Swagger/FastAPI:

```text
http://IP_DO_SERVIDOR:8000/docs
```

Credenciais iniciais:

Email e senha dependem das variáveis ADMIN_EMAIL e ADMIN_PASSWORD configuradas no .env.

## Firewall

Se usar `ufw`:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw reload
```

Em servidores de nuvem, libere tambem as portas no painel do provedor.

## Atualizar Sistema

Depois de enviar novas alteracoes:

```bash
cd /opt/ferias-onrtdpj
docker compose up -d --build
```

Opcional, limpar imagens antigas:

```bash
docker image prune -f
```

## Parar e Reiniciar

Parar:

```bash
docker compose down
```

Iniciar:

```bash
docker compose up -d
```

Reiniciar:

```bash
docker compose restart
```

Nao use `docker compose down -v` sem backup, porque isso remove volumes e pode apagar o banco.

## Backup do Banco e Documentos

Crie a pasta de backups:

```bash
mkdir -p backups
```

Faca backup:

```bash
docker compose exec -T db pg_dump -U ferias ferias > backups/ferias-$(date +%F).sql
```

Esse comando gera um dump SQL do PostgreSQL.

Os documentos ficam na pasta `uploads/`. Para gerar um arquivo compactado com os uploads:

```bash
tar czf backups/documentos-$(date +%F).tar.gz uploads
```

## Restaurar Backup

Restaure o backup:

```bash
cat backups/ferias-AAAA-MM-DD.sql | docker compose exec -T db psql -U ferias -d ferias
```

Para restauracoes em ambientes reais, prefira parar o backend durante a operacao e valide o backup antes de sobrescrever dados.

## HTTPS com Proxy Reverso

Para producao, use HTTPS.

Arquitetura comum:

```text
Internet
  -> Nginx, Traefik ou Caddy com HTTPS
    -> frontend:80
    -> backend:8000
```

Exemplo de dominios:

```text
https://ferias.seudominio.com
https://api-ferias.seudominio.com
```

Configure `.env` antes do build:

```env
FRONTEND_URL=https://ferias.seudominio.com
VITE_API_URL=https://api-ferias.seudominio.com
```

Rebuild:

```bash
docker compose up -d --build
```

## Comandos Uteis

Status:

```bash
docker compose ps
```

Logs:

```bash
docker compose logs -f
```

Logs do backend:

```bash
docker compose logs -f backend
```

Versao atual das migrations no banco:

```bash
docker compose exec backend alembic current
```

Logs do frontend:

```bash
docker compose logs -f frontend
```

Entrar no backend:

```bash
docker compose exec backend sh
```

Entrar no frontend:

```bash
docker compose exec frontend sh
```

Rebuild sem cache:

```bash
docker compose build --no-cache
docker compose up -d
```

Ver uso de disco:

```bash
docker system df
```

## Problemas Comuns

### Frontend abre, mas login falha

Provavel causa: `VITE_API_URL` incorreto.

Corrija `.env`:

```env
VITE_API_URL=http://IP_DO_SERVIDOR:8000
```

Rebuild:

```bash
docker compose up -d --build
```

### API nao abre na porta 8000

Confira containers:

```bash
docker compose ps
```

Confira logs:

```bash
docker compose logs backend
```

Confira firewall:

```bash
sudo ufw status
```

### Porta 80 ja esta em uso

Altere `.env`:

```env
FRONTEND_PORT=8080
```

Suba novamente:

```bash
docker compose up -d
```

Acesse:

```text
http://IP_DO_SERVIDOR:8080
```

### Alterei `.env`, mas o frontend continua chamando URL antiga

O Vite embute `VITE_API_URL` no build.

Rode:

```bash
docker compose up -d --build
```

## Checklist de Producao

- [ ] Trocar `SECRET_KEY`.
- [ ] Trocar `CREDENTIALS_ENCRYPTION_KEY`.
- [ ] Trocar senha inicial do admin.
- [ ] Configurar IP ou dominio.
- [ ] Conferir `VITE_API_URL`.
- [ ] Liberar portas no firewall.
- [ ] Testar login.
- [ ] Testar cadastro de usuario.
- [ ] Testar solicitacao de ferias.
- [ ] Testar calendario de disponibilidade.
- [ ] Testar exportacao de logs e relatorios.
- [ ] Configurar backup do volume `ferias_data`.
- [ ] Configurar backup da pasta `uploads/`.
- [ ] Configurar HTTPS para uso real.
