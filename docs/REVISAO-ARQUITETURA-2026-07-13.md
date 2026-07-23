# Revisão completa de arquitetura e código — 13/07/2026

## Resultado geral

O projeto evoluiu bem e apresenta uma arquitetura coerente, especialmente no novo módulo de Patrimônios e Autorizações. Ainda não considero o conjunto pronto para produção sem corrigir os riscos prioritários descritos neste documento.

Esta revisão foi somente diagnóstica. Nenhuma correção de código foi realizada durante a análise.

## Achados prioritários

### Alta — Desativação pode bloquear permanentemente uma autorização

A desativação do colaborador não verifica vínculos ou autorizações abertas em `backend/app/services/users_service.py`.

Se ele for desativado enquanto estiver em `aguardando_aceite`:

- não poderá mais autenticar;
- somente o próprio titular pode aceitar;
- o administrador não pode cancelar nesse estado;
- a devolução só aceita o status `entregue`;
- o vínculo não pode ser encerrado enquanto a autorização estiver aberta.

Recomendação: bloquear a desativação enquanto existirem fluxos abertos ou implementar um processo administrativo de desligamento que encerre solicitações, reservas e vínculos com justificativa auditável.

### Alta — IP do aceite pode registrar o proxy, não o colaborador

O aceite e o limite de login usam `request.client.host` em:

- `backend/app/routers/auth.py`;
- `backend/app/services/autorizacoes_equipamentos_service.py`.

O Nginx encaminha `X-Forwarded-For`, mas o Uvicorn não possui uma configuração explícita de proxies confiáveis. O termo pode acabar registrando o IP interno do container Nginx.

Recomendações:

- restringir o backend para não ficar diretamente público;
- configurar explicitamente os proxies confiáveis;
- validar o IP real em teste integrado;
- não usar `FORWARDED_ALLOW_IPS=*` enquanto a porta 8000 estiver exposta publicamente.

### Alta — Recuperação de versões históricas do termo está incompleta

O serviço trabalha apenas com a versão atual `v2` e rejeita outra versão durante a renderização normal.

A regeneração de um `v1` funciona quando existe snapshot HTML. Porém, se um termo `v1` falhou antes de salvar o snapshot, não poderá ser reconstruído depois da mudança para `v2`.

Também foi observado que:

- `v1` e `v2` permanecem marcadas como ativas;
- a primeira criação concorrente da versão atual pode disputar a restrição única;
- a versão é criada em tempo de execução, não por migração controlada.

Recomendação: criar um registro de templates por código, carregar o template correspondente à versão histórica, manter somente uma versão vigente e semear novas versões por migração ou bootstrap concorrente seguro.

## Achados médios

### Listagem administrativa sem paginação

A listagem administrativa de autorizações não possui paginação. Ela também executa uma consulta detalhada por solicitação e retorna cláusulas e eventos completos em cada item. Isso tende a ficar lento conforme o histórico crescer.

Recomendação: criar DTO resumido para a tabela, endpoint de detalhe separado e paginação no backend.

### Ausência de testes integrados

Os testes do backend são majoritariamente unitários com objetos simulados. Não existem testes automatizados HTTP/PostgreSQL. O erro anterior com `SELECT DISTINCT` passou pela suíte por esse motivo.

O frontend não possui scripts de testes ou lint. Fluxos críticos como aprovação, aceite, PDF e devolução dependem de testes manuais.

Recomendações:

- testes de integração com PostgreSQL real;
- testes dos endpoints FastAPI;
- testes de concorrência para reservas e vínculos;
- React Testing Library para componentes;
- Playwright ou equivalente para os fluxos principais;
- ESLint no frontend e análise estática no backend.

### Proteção e validação de dados pessoais

Telefones de emergência continuam em texto puro no banco, enquanto CPF, endereço e dados bancários são criptografados.

O backend também não valida efetivamente os formatos de telefone e CEP. Além disso, `UserUpdate` permite enviar endereço ou dados bancários parcialmente preenchidos, divergindo da obrigatoriedade aplicada no cadastro.

Recomendações:

- criptografar telefones de emergência;
- validar telefone e CEP no backend;
- aplicar as mesmas regras estruturadas no cadastro e na edição;
- preparar migração controlada dos registros existentes.

### Configuração de cookie em produção

O Compose define `ENVIRONMENT=production`, mas deixa `COOKIE_SECURE=false` por padrão. A documentação explica a configuração, porém a aplicação deveria falhar de forma segura quando uma implantação de produção estiver mal configurada.

### Healthcheck superficial

O healthcheck do backend consulta somente `/`, que retorna uma resposta estática. O container pode ficar marcado como saudável mesmo sem conexão funcional com PostgreSQL ou acesso ao armazenamento.

Recomendação: separar endpoints de liveness e readiness, incluindo `SELECT 1` e verificação controlada do diretório de uploads.

### Rate limit local ao processo

O limite de tentativas de login é mantido em memória. Ele é perdido em reinicializações e não funciona de forma global com múltiplas réplicas.

Recomendação: armazenar o controle em Redis ou solução compartilhada equivalente.

### Autorização excessivamente ampla

O perfil `admin` concentra RH, dados bancários, documentos, patrimônio e aprovações. Também é possível um administrador aprovar a própria solicitação.

Recomendação: avaliar papéis separados, como RH, patrimônio/TI, financeiro e auditoria, além de aprovação por uma segunda pessoa quando exigido pela política interna.

## Melhorias menores

- Padronizar datas como `DateTime(timezone=True)`; módulos antigos ainda usam `datetime.utcnow` sem timezone.
- Dividir os serviços de autorizações e termos, atualmente muito extensos.
- Adicionar auditoria para visualização e download de documentos sensíveis.
- Adicionar antivírus ou sanitização aos PDFs e imagens enviados.
- Configurar `.gitattributes` para eliminar os avisos recorrentes de conversão LF/CRLF.
- Garantir que todos os arquivos novos sejam incluídos no commit correto.

## Pontos positivos

- Boa separação entre routers, schemas, services, repositories e storage.
- Locks e índices parciais para proteger vínculos e reservas concorrentes.
- CPF com validação, criptografia e índice HMAC.
- Endereços, dados bancários e snapshots HTML criptografados.
- Histórico auditável de equipamentos e autorizações.
- PDFs versionados e preservados por snapshot.
- Proteção contra travessia de diretórios.
- Uploads com limite, MIME permitido e validação de assinatura.
- Backend executado como usuário não-root.
- CSP e cabeçalhos de segurança no Nginx.
- Documentação operacional e de recuperação bem desenvolvida.

## Validações executadas

- 213 testes do backend aprovados.
- Build Vite aprovado, com 160 módulos transformados.
- `alembic check` sem divergências entre modelos e migrações.
- `docker compose config --quiet` aprovado.
- Smoke autenticado de patrimônios, autorizações e documentos com HTTP 200.
- `git diff --check` sem erros.
- `.env` ignorado e nenhum segredo real encontrado nos arquivos rastreáveis.

## Ordem recomendada para as próximas correções

1. Resolver o bloqueio causado pela desativação de colaboradores com autorizações abertas.
2. Corrigir a captura do IP atrás dos proxies.
3. Completar o suporte a versões históricas dos termos.
4. Adicionar paginação e DTOs resumidos às listagens.
5. Criar testes integrados HTTP/PostgreSQL e testes do frontend.
6. Reforçar criptografia, validação e RBAC.
