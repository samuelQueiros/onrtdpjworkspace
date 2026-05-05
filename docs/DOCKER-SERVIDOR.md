# Guia de Docker em Servidor

Este guia explica como publicar o Sistema de Gestao de Ferias ONRTDPJ em um servidor usando Docker e Docker Compose.

## Visao Geral

O Docker Compose sobe dois servicos:

| Servico | Container | Porta | Funcao |
|---|---|---|---|
| `backend` | `ferias-backend` | `8000` | API FastAPI |
| `frontend` | `ferias-frontend` | `80` | Interface React servida por Nginx |

O banco SQLite fica em um volume Docker:

```text
ferias_data:/app/data/ferias.db
```

Isso evita perder o banco ao recriar containers.

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
SECRET_KEY=troque-por-uma-chave-longa-e-segura
ACCESS_TOKEN_EXPIRE_MINUTES=480

FRONTEND_URL=http://123.123.123.123
VITE_API_URL=http://123.123.123.123:8000

FRONTEND_PORT=80
BACKEND_PORT=8000
```

Exemplo usando dominio:

```env
SECRET_KEY=troque-por-uma-chave-longa-e-segura
ACCESS_TOKEN_EXPIRE_MINUTES=480

FRONTEND_URL=https://ferias.seudominio.com
VITE_API_URL=https://api-ferias.seudominio.com

FRONTEND_PORT=80
BACKEND_PORT=8000
```

Importante:

- `VITE_API_URL` precisa ser acessivel pelo navegador dos usuarios.
- Nao use `chat-server` em producao, a menos que o sistema seja acessado apenas na propria maquina.
- Se alterar `VITE_API_URL`, e necessario rebuildar o frontend.

## Subir o Sistema

Na raiz do projeto:

```bash
docker compose up -d --build
```

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

```text
Email: admin@sistema.com
Senha: admin123
```

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

## Backup do Banco

Descubra o nome do volume:

```bash
docker volume ls
```

O nome geralmente sera algo como:

```text
ferias-onrtdpj_ferias_data
```

Crie a pasta de backups:

```bash
mkdir -p backups
```

Faca backup:

```bash
docker run --rm \
  -v ferias-onrtdpj_ferias_data:/data \
  -v "$(pwd)/backups:/backup" \
  alpine \
  cp /data/ferias.db /backup/ferias-$(date +%F).db
```

Se o nome do volume for diferente, substitua `ferias-onrtdpj_ferias_data`.

## Restaurar Backup

Pare os containers:

```bash
docker compose down
```

Copie o backup para o volume:

```bash
docker run --rm \
  -v ferias-onrtdpj_ferias_data:/data \
  -v "$(pwd)/backups:/backup" \
  alpine \
  cp /backup/ferias-AAAA-MM-DD.db /data/ferias.db
```

Suba novamente:

```bash
docker compose up -d
```

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
- [ ] Configurar HTTPS para uso real.
