# Operação e preparação para AWS

Este projeto continua sendo desenvolvido e validado localmente. Este documento
separa o que já pode ser testado agora do que depende da futura infraestrutura
AWS. MFA não faz parte do escopo atual.

## Validação local antes de integrar uma mudança

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest discover -s tests
.\venv\Scripts\python.exe -m pip_audit -r requirements.txt
alembic heads

cd ..\frontend
npm ci
npm test -- --run
npm run lint
npm run build
npm audit --audit-level=critical

cd ..
docker compose config
docker compose build
docker compose up -d
```

Confirme `GET /health/live` e `GET /health/ready`. A migration roda no serviço
de execução única `migrate`; uma falha impede o backend de iniciar.

## Publicação e rollback

Antes de publicar:

1. gere `.\scripts\backup.ps1`;
2. registre o commit e a imagem que estão em execução;
3. valide a migration em uma cópia recente do banco;
4. execute `docker compose up --build -d`;
5. valide health checks, login, upload/download e uma operação de férias.

Para rollback de aplicação, volte à imagem/commit anterior e suba novamente os
serviços. Não execute `alembic downgrade` automaticamente: migrations
destrutivas exigem procedimento específico e backup validado. Se a migration
alterou dados de forma incompatível, restaure o pacote:

```powershell
.\scripts\restore.ps1 -BackupFile .\backups\ferias-AAAAMMDD-HHMMSS.zip
```

O restore valida SHA-256, cria um backup de segurança, pausa o backend, restaura
o banco, aplica as migrations atuais e recupera uploads. Os uploads anteriores
são preservados em uma pasta `uploads.pre-restore-*`.

## Segredos e configuração de produção

Em produção, `SECRET_KEY` e `CREDENTIALS_ENCRYPTION_KEY` devem ser aleatórias,
distintas e ter pelo menos 32 caracteres. A senha inicial do administrador deve
ter pelo menos 12 caracteres. Credenciais padrão de PostgreSQL são rejeitadas.
Não versionar `.env`, dumps, uploads ou checksums.

O rate limit local protege combinações IP/conta, IP isolado e conta isolada. Ele
é deliberadamente local ao processo. Antes de escalar para mais de uma réplica,
substitua-o por armazenamento compartilhado ou aplique limitação equivalente
no gateway/WAF.

## Itens que dependem da futura AWS

- Definir a topologia (por exemplo: ALB + ECS/Fargate, RDS PostgreSQL e S3).
- Armazenar segredos no Secrets Manager ou Parameter Store com KMS.
- Migrar uploads do volume local para S3, com versionamento, criptografia,
  política de retenção e teste de restauração.
- Colocar banco e tarefas em sub-redes privadas e restringir security groups.
- Habilitar TLS público, redirecionamento HTTP/HTTPS e política HSTS no ALB.
- Configurar WAF/rate limiting distribuído e proteção contra abuso.
- Enviar logs e métricas ao CloudWatch com alarmes de 5xx, latência, CPU,
  memória, conexões do banco, espaço e falhas de backup.
- Configurar snapshots automáticos do RDS, PITR e ensaios periódicos de restore.
- Criar staging isolado e pipeline que promova imagens imutáveis já testadas.
- Definir autoscaling e ajustar o pool considerando
  `réplicas × workers × (pool_size + max_overflow)`.

## Exceção temporária de dependência frontend

O projeto usa React Router apenas no modo declarativo (`BrowserRouter`,
`Routes`, `Route`, `Link` e `useNavigate`). A versão `7.18.2` corrige os
advisories aplicáveis a esse modo. Em 31/07/2026, o `npm audit` ainda relata um
advisory high exclusivo do modo RSC e aponta como correção uma versão ainda não
publicada. Por isso o CI bloqueia vulnerabilidades críticas e esta exceção deve
ser revista assim que uma versão corrigida estiver disponível.
