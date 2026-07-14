# Patrimônios e autorizações de equipamentos

Este documento descreve o módulo de inventário, vínculo de bens, autorização para home office, entrega, aceite eletrônico, emissão do termo e devolução.

## Escopo

O módulo permite:

- cadastrar, editar, vincular, desvincular, colocar em manutenção e baixar equipamentos;
- preservar o histórico de responsáveis por cada bem;
- solicitar itens já vinculados ou um item disponível diferente;
- aprovar integral ou parcialmente, rejeitar e cancelar solicitações;
- registrar entrega e aceite como eventos distintos;
- emitir um PDF definitivo a partir de dados históricos congelados;
- registrar devolução, ausências e estado de conservação;
- integrar pendências às aprovações e o termo ao módulo de documentos.

Não há upload de fotografias. O estado de conservação é textual.

## Arquitetura

O backend mantém a separação utilizada no restante do projeto:

| Camada | Responsabilidade |
|---|---|
| `models/patrimonio.py` | Entidades, relacionamentos, índices e estados |
| `schemas/patrimonio.py` | DTOs de entrada e saída e validações estruturais |
| `repositories/patrimonios_repository.py` | Consultas, locks e persistência |
| `services/patrimonios_service.py` | Inventário, vínculos, manutenção e baixa |
| `services/autorizacoes_equipamentos_service.py` | Solicitação, decisão, entrega, aceite e devolução |
| `services/termos_equipamentos_service.py` | Versão do termo, HTML, PDF e integração com `Documento` |
| `storage/termos_storage.py` | Nome seguro, caminho, escrita atômica e idempotência |
| `routers/patrimonios.py` | API administrativa e consultas do colaborador |
| `routers/autorizacoes_equipamentos.py` | API do fluxo de autorização |
| `templates/termos_equipamentos/v1.html` | Versão histórica `v1`, preservada para auditoria |
| `templates/termos_equipamentos/v2.html` | Conteúdo e identidade visual corrigida da versão vigente `v2` |

O frontend mantém páginas, componentes, serviços de API e CSS separados por domínio. Regras de acesso e transições são sempre validadas novamente no backend.

## Modelo de dados

A migration `20260713_0007_patrimonios_autorizacoes.py` adiciona:

| Tabela/campo | Finalidade |
|---|---|
| `users.cpf_criptografado` | CPF cifrado para operações autorizadas |
| `users.cpf_hash` | Índice HMAC-SHA256 único para detectar duplicidade sem pesquisar o texto cifrado |
| `equipamentos` | Cadastro atual do bem e sua disponibilidade |
| `equipamento_vinculos` | Histórico temporal de responsáveis pelo bem |
| `equipamento_eventos` | Manutenção, baixa e demais mudanças auditáveis do inventário |
| `termo_equipamento_versoes` | Código, vigência, hash e template/cláusulas imutáveis do termo |
| `solicitacoes_equipamentos` | Cabeçalho, decisões, entrega, aceite, documento e devolução |
| `solicitacoes_equipamentos.termo_html_snapshot_criptografado` | HTML exato aceito pelo colaborador, cifrado para regeneração histórica |
| `solicitacao_equipamento_itens` | Itens, reservas e snapshots históricos |
| `solicitacao_equipamento_eventos` | Linha do tempo da solicitação |

Um vínculo está ativo quando `desvinculado_em IS NULL`. Um índice único parcial no PostgreSQL impede dois vínculos ativos para o mesmo equipamento.

Cada solicitação guarda snapshots do nome, CPF cifrado, cargo e departamento. Cada item guarda patrimônio, série, tipo, marca/modelo, conservação e observações. Depois do aceite, o HTML efetivamente usado no termo é congelado em `termo_html_snapshot_criptografado`. Alterações posteriores no cadastro, no equipamento ou no template não alteram o termo histórico.

## Estados

### Equipamento

| Estado | Significado |
|---|---|
| `disponivel` | Ativo, sem vínculo ou reserva e apto para solicitação |
| `vinculado` | Sob responsabilidade de um colaborador |
| `reservado` | Separado por uma autorização aprovada e ainda não entregue |
| `manutencao` | Indisponível até finalização da manutenção |
| `baixado` | Desativado; não pode ser solicitado ou vinculado |

### Solicitação

Fluxo normal:

```text
pendente
  -> rejeitada
  -> cancelada
  -> aguardando_entrega
       -> aguardando_aceite
            -> aceite_registrado_aguardando_documento
                 -> entregue
                      -> devolvida
```

| Estado | Evento que o produz |
|---|---|
| `pendente` | Colaborador envia a solicitação |
| `aguardando_entrega` | Administrador aprova ao menos um item |
| `aguardando_aceite` | Administrador registra a entrega de todos os itens aprovados |
| `aceite_registrado_aguardando_documento` | Dono da solicitação confirma o aceite; PDF ainda está sendo consolidado |
| `entregue` | PDF definitivo foi gerado e associado ao módulo de documentos |
| `rejeitada` | Administrador rejeita com motivo obrigatório |
| `cancelada` | Solicitação é cancelada dentro das regras do estado atual |
| `devolvida` | Administrador registra a situação de todos os itens entregues |

O valor `aprovada` existe no catálogo de estados para compatibilidade do domínio, mas o fluxo atual avança diretamente de `pendente` para `aguardando_entrega` após a decisão administrativa.

O status do documento é separado: `pendente`, `gerando`, `gerado` ou `falha`. Uma falha de PDF não apaga o aceite e pode ser recuperada pela regeneração administrativa.

## Permissões

| Operação | Colaborador | Administrador |
|---|---:|---:|
| Consultar os próprios equipamentos | Sim | Sim |
| Consultar equipamentos disponíveis para solicitação | Sim | Sim |
| Administrar inventário e vínculos | Não | Sim |
| Criar solicitação e consultar o próprio histórico | Sim | Sim, para a própria conta |
| Consultar qualquer solicitação | Não | Sim |
| Cancelar solicitação própria pendente | Sim | Sim, conforme estado e justificativa |
| Aprovar, ajustar itens ou rejeitar | Não | Sim |
| Registrar entrega, devolução ou regenerar PDF | Não | Sim |
| Registrar aceite | Somente o dono autenticado | Não em nome de outro colaborador |
| Visualizar/baixar o termo | Dono do documento | Sim |

Ocultar ações na interface não substitui a autorização nas dependências e nos services do backend.

## API resumida

Todos os endpoints exigem autenticação. Os marcados como administrativos usam a validação `require_admin`.

### Patrimônios

| Método | Endpoint | Acesso | Resumo |
|---|---|---|---|
| `GET` | `/patrimonios` | Admin | Lista paginada; filtros `busca`, `tipo`, `status`, `ativo`, `user_id`, `page` e `page_size` |
| `POST` | `/patrimonios` | Admin | Cadastra equipamento |
| `GET` | `/patrimonios/me` | Autenticado | Itens atualmente vinculados ao usuário |
| `GET` | `/patrimonios/disponiveis` | Autenticado | Apenas itens ativos e disponíveis |
| `GET` | `/patrimonios/{id}` | Admin | Detalhes, vínculo atual e histórico |
| `PUT` | `/patrimonios/{id}` | Admin | Edita o cadastro |
| `POST` | `/patrimonios/{id}/vinculos` | Admin | Vincula colaborador e registra eventual exceção de segunda máquina |
| `POST` | `/patrimonios/{id}/desvincular` | Admin | Encerra o vínculo ativo |
| `POST` | `/patrimonios/{id}/manutencao` | Admin | Inicia manutenção |
| `POST` | `/patrimonios/{id}/finalizar-manutencao` | Admin | Finaliza manutenção |
| `POST` | `/patrimonios/{id}/baixa` | Admin | Baixa e desativa o equipamento |

### Autorizações

| Método | Endpoint | Acesso | Resumo |
|---|---|---|---|
| `POST` | `/autorizacoes-equipamentos` | Autenticado | Solicita uma lista única de equipamentos |
| `GET` | `/autorizacoes-equipamentos/me` | Autenticado | Histórico do usuário |
| `GET` | `/autorizacoes-equipamentos/admin` | Admin | Filtros por status, usuário, equipamento e período |
| `GET` | `/autorizacoes-equipamentos/{id}` | Dono/Admin | Detalhes e eventos |
| `POST` | `/autorizacoes-equipamentos/{id}/cancelar` | Dono/Admin | Cancela dentro das regras de transição |
| `POST` | `/autorizacoes-equipamentos/{id}/aprovar` | Admin | Aprovação integral ou parcial por IDs de itens |
| `POST` | `/autorizacoes-equipamentos/{id}/rejeitar` | Admin | Rejeita com motivo obrigatório |
| `POST` | `/autorizacoes-equipamentos/{id}/entrega` | Admin | Registra responsável, local, conservação e todos os itens |
| `POST` | `/autorizacoes-equipamentos/{id}/aceite` | Dono | Registra aceite, local, IP e request ID do backend |
| `POST` | `/autorizacoes-equipamentos/{id}/devolucao` | Admin | Registra cada item como devolvido ou ausente |
| `POST` | `/autorizacoes-equipamentos/{id}/documento/regenerar` | Admin | Recupera falha usando a mesma versão histórica |
| `GET` | `/aprovacoes/pendencias` | Admin | Contagem de férias, equipamentos e total |

Os schemas completos e os códigos HTTP estão também no Swagger em `/docs` e na referência [API.md](API.md).

## Regras de integridade e concorrência

- patrimônio e série são únicos quando informados;
- equipamento inativo, baixado, em manutenção, reservado ou já vinculado não pode ser oferecido como disponível;
- solicitações não aceitam itens repetidos nem lista vazia;
- itens são revalidados sob lock na aprovação e na entrega;
- a reserva ativa possui índice único parcial por equipamento;
- locks de linha do PostgreSQL e índices únicos parciais protegem decisões concorrentes;
- uma máquina principal adicional exige autorização e justificativa administrativas explícitas;
- aprovação parcial marca itens removidos e preserva o motivo no histórico;
- rejeição exige justificativa;
- operações fora do estado esperado retornam erro de domínio;
- baixa e trocas de responsável preservam histórico em vez de apagar registros.

## PDF, versão e hash

A versão vigente `v2` usa Jinja2 para preencher HTML/CSS confiável e WeasyPrint para produzir o PDF. Ela substitui CSS Grid por Flexbox com dimensões explícitas, evitando o colapso das áreas de identificação e assinaturas no renderizador. O template mantém as cláusulas da `v1`, e os dados dinâmicos são escapados automaticamente.

No registro da entrega, `garantir_versao_termo()` cria ou recupera `termo_equipamento_versoes` e associa a versão à solicitação antes de o colaborador visualizar e aceitar. O registro contém:

- código vigente `v2`, mantendo a `v1` histórica;
- data de vigência;
- template/cláusulas completos;
- SHA-256 calculado sobre o template com quebras de linha canônicas e o logotipo.

Alterar `v2.html` ou o logotipo sem incrementar o código causa erro. Para uma mudança futura, deve-se criar `v3.html`, preservar as versões anteriores e manter a capacidade de recuperar versões históricas.

O termo usa somente snapshots e datas oficiais do backend. A hora é armazenada em UTC e apresentada no PDF em `America/Sao_Paulo`. O nome segue o padrão:

```text
termo-equipamentos-nome-colaborador-solicitacao-123-v2.pdf
```

O arquivo é integrado como `Documento.tipo = termo_equipamentos`, pertence ao colaborador e não pode ser excluído pela exclusão genérica de documentos. O dono e administradores podem usar as rotas existentes de visualização e download.

Na primeira geração, o backend cifra o HTML congelado com Fernet e persiste somente o valor protegido em `termo_html_snapshot_criptografado`. A regeneração administrativa descriptografa esse snapshot e renderiza novamente o mesmo conteúdo; ela não consulta o cadastro atual nem recompõe o documento a partir do template vigente. O HTML em claro existe apenas em memória durante a geração do PDF e não deve ser escrito em logs.

O sistema registra evidências técnicas de aceite, mas não afirma que esse aceite equivale a assinatura digital ou certificação legal.

## Armazenamento e recuperação

Os termos ficam em:

```text
uploads/termos-equipamentos/nome-colaborador/solicitacao-123/
  termo-equipamentos-nome-colaborador-solicitacao-123-v2.pdf
```

A gravação ocorre em arquivo temporário no mesmo diretório, seguida de `fsync` e `os.replace`. Assim, leitores não recebem um PDF parcial. Se o hash do PDF existente for igual, uma chamada repetida não reescreve o arquivo. A regeneração reutiliza o mesmo registro `Documento` e o mesmo caminho, mantendo uma única linha histórica.

Banco e filesystem não formam uma transação distribuída. Falhas tratadas ficam com `documento_status = falha`; uma interrupção abrupta também pode deixar o status pendente. Em ambos os casos, o aceite permanece registrado e o administrador pode executar a regeneração idempotente.

## Dados sensíveis e privacidade

- o backend valida formato e dígitos verificadores;
- `cpf_hash` é um HMAC-SHA256 usado para unicidade;
- `cpf_criptografado` usa o mecanismo Fernet derivado de `CREDENTIALS_ENCRYPTION_KEY`;
- `termo_html_snapshot_criptografado` usa o mesmo mecanismo, pois contém CPF completo e outras evidências do aceite;
- endereços novos ou novamente salvos e dados bancários são serializados como JSON e cifrados em repouso; a leitura de endereços legados em texto é mantida para compatibilidade, e esses registros devem ser recifrados por uma migração operacional controlada ou na próxima edição do cadastro;
- listagens comuns recebem somente CPF mascarado;
- CPF completo é restrito a operações administrativas auditadas e à geração do termo;
- o PDF definitivo permanece no armazenamento do módulo de documentos e é protegido pelas mesmas regras de acesso: somente o dono e administradores podem visualizá-lo ou baixá-lo;
- logs não devem conter CPF, conteúdo cifrado ou dados bancários;
- usuários antigos podem permanecer com CPF nulo após a migration, mas precisam completar o cadastro antes de solicitar equipamentos;
- a chave de criptografia precisa fazer parte do plano seguro de backup. Sua perda impede recuperar CPFs, snapshots históricos dos termos, endereços, dados bancários e outros dados protegidos.

Uma troca de `CREDENTIALS_ENCRYPTION_KEY` exige migração controlada dos dados cifrados e dos índices HMAC; não basta alterar a variável no servidor.

## Migração e deploy

Antes da atualização:

1. faça backup do PostgreSQL, de `uploads/` e da chave de criptografia;
2. valide que o servidor pode reconstruir a imagem Docker;
3. publique o código sem alterar migrations antigas;
4. reconstrua e suba os serviços:

```bash
docker compose up -d --build
```

O backend executa `alembic upgrade head` antes de iniciar. Para aplicar ou conferir manualmente:

```bash
docker compose run --rm --entrypoint alembic backend upgrade head
docker compose exec backend alembic current
```

A imagem do backend agora inclui Jinja2, WeasyPrint, Pango, HarfBuzz e fontes DejaVu. Um deploy que reutilize uma imagem antiga não conseguirá gerar PDFs; é necessário rebuild.

Após subir:

```bash
docker compose ps
docker compose logs backend
```

Faça um teste controlado com cadastro, vínculo, aprovação, entrega, aceite, download do PDF e devolução. Não execute downgrade da migration em produção sem um plano de restauração, pois ele remove as tabelas e o CPF cifrado.

## Backup

O backup completo precisa preservar juntos:

- dump PostgreSQL, que contém histórico, snapshots, versão e referência ao documento;
- pasta `uploads/`, que contém o PDF definitivo;
- `CREDENTIALS_ENCRYPTION_KEY`, guardada em cofre separado do dump.

Exemplo Linux:

```bash
mkdir -p backups
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > backups/ferias-$(date +%F).dump
tar czf backups/documentos-$(date +%F).tar.gz uploads
```

Teste periodicamente a restauração em ambiente isolado. Restaurar apenas o banco deixa documentos ausentes; restaurar apenas `uploads/` deixa arquivos sem autorização ou metadados.

## Auditoria

São registrados eventos e logs para cadastro/edição, vínculo/desvínculo, manutenção, baixa, criação/cancelamento, decisão e ajuste de itens, rejeição, entrega, aceite, falha/geração/regeneração de PDF, devolução e consulta administrativa de CPF completo.

Logs devem identificar ator, solicitação ou equipamento e resultado, sem reproduzir dados pessoais desnecessários.

## Validação de RH, jurídico e produto

O conteúdo jurídico foi preservado a partir do documento fornecido; o sistema apenas estruturou dados, etapas e evidências técnicas. Antes do uso oficial, RH e jurídico devem validar expressamente:

- desconto em folha e formas de autorização;
- ressarcimento, depreciação e valor de reposição;
- advertências, suspensão e demais penalidades disciplinares;
- tratamento de perda, furto e roubo;
- suficiência das evidências e validade do aceite eletrônico;
- retenção, acesso e descarte de CPF, IP, logs e PDFs.

O PDF atual não possui assinatura digital ICP-Brasil nem certificação PDF/A validada. Essas características não devem ser anunciadas sem decisão jurídica e implementação específica.
