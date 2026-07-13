# Documentacao da API

Base URL local:

```text
http://chat-server:8000
```

Documentacao interativa:

```text
http://chat-server:8000/docs
```

## Autenticacao

O frontend usa um cookie de sessão `HttpOnly`, definido no login. Clientes de API também podem usar o header:

```http
Authorization: Bearer <access_token>
```

## Health Check

### GET `/`

Retorna status da API.

Resposta:

```json
{
  "status": "ok",
  "message": "API de Gestao de Ferias rodando"
}
```

## Auth

### POST `/auth/login`

Realiza login OAuth2 e retorna `access_token` para Swagger, scripts e integrações.

Content-Type:

```text
application/x-www-form-urlencoded
```

Campos:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `username` | string | Sim | Email do usuario |
| `password` | string | Sim | Senha |

Exemplo:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://chat-server:8000/auth/login `
  -Body @{username='SEU_ADMIN_EMAIL';password='SUA_SENHA_ADMIN'}
```

Resposta:

```json
{
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@sistema.com",
    "role": "admin",
    "dias_totais": 30,
    "dias_restantes": 30
  }
}
```

### POST `/auth/session`

Realiza o login da aplicação web e grava o token em cookie `HttpOnly`. A resposta não expõe o token ao JavaScript.

### POST `/auth/logout`

Encerra a sessão e remove o cookie de autenticação.

### POST `/auth/logout-all`

Revoga todos os tokens emitidos anteriormente para o usuário autenticado.

## Logs

`GET /logs?page=1&page_size=50` retorna `items`, `page`, `page_size` e `total`. O tamanho máximo da página é 200.

## Cargos

- `GET /cargos`: lista cargos para usuários autenticados.
- `POST /cargos`: cria um cargo (administrador).
- `PUT /cargos/{id}`: renomeia um cargo (administrador).
- `DELETE /cargos/{id}`: exclui um cargo e remove os vínculos (administrador).

## Dados sensíveis de colaboradores

`GET /users/{id}/dados-sensiveis` é restrito a administradores. Dados bancários são armazenados criptografados e não são retornados na listagem geral de usuários.

### GET `/auth/me`

Retorna o usuario autenticado.

Acesso: autenticado.

Resposta:

```json
{
  "id": 1,
  "nome": "Administrador",
  "email": "admin@sistema.com",
  "role": "admin",
  "dias_totais": 30,
  "dias_restantes": 30
}
```

## Ferias

### GET `/ferias/me`

Lista ferias do usuario autenticado.

Acesso: autenticado.

Resposta:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "data_inicio": "2026-05-05",
    "data_fim": "2026-05-19",
    "dias_usados": 15,
    "criado_em": "2026-05-05T14:00:00"
  }
]
```

### GET `/ferias/disponibilidade`

Retorna ferias marcadas por todos os colaboradores e periodos bloqueados.

Acesso: autenticado.

Resposta:

```json
{
  "periodos_bloqueados": [
    {
      "data_inicio": "2026-05-10",
      "data_fim": "2026-05-15"
    }
  ],
  "ferias_marcadas": [
    {
      "id": 1,
      "user_id": 1,
      "nome": "Administrador",
      "data_inicio": "2026-05-05",
      "data_fim": "2026-05-19",
      "dias_usados": 15
    }
  ]
}
```

### POST `/ferias`

Registra novo periodo de ferias para o usuario autenticado.

Acesso: autenticado.

Body:

```json
{
  "data_inicio": "2026-06-01",
  "data_fim": "2026-06-15"
}
```

Validacoes:

- `data_fim` deve ser maior ou igual a `data_inicio`.
- Usuario deve possuir saldo suficiente.
- Periodo nao pode violar o limite de colaboradores simultaneos.

Resposta:

```json
{
  "id": 2,
  "user_id": 1,
  "data_inicio": "2026-06-01",
  "data_fim": "2026-06-15",
  "dias_usados": 15,
  "criado_em": "2026-05-05T14:00:00"
}
```

### PUT `/ferias/{ferias_id}`

Edita periodo de ferias.

Acesso:

- Usuario comum: apenas suas proprias ferias.
- Admin: qualquer ferias.

Body:

```json
{
  "data_inicio": "2026-06-02",
  "data_fim": "2026-06-16"
}
```

Resposta:

```json
{
  "id": 2,
  "user_id": 1,
  "data_inicio": "2026-06-02",
  "data_fim": "2026-06-16",
  "dias_usados": 15,
  "criado_em": "2026-05-05T14:00:00"
}
```

### DELETE `/ferias/{ferias_id}`

Cancela periodo de ferias.

Acesso:

- Usuario comum: apenas suas proprias ferias.
- Admin: qualquer ferias.

Resposta:

```json
{
  "detail": "Ferias canceladas com sucesso"
}
```

## Usuarios

### GET `/users`

Lista usuarios.

Acesso: admin.

Resposta:

```json
[
  {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@sistema.com",
    "role": "admin",
    "dias_totais": 30,
    "dias_restantes": 30,
    "criado_em": "2026-05-05T14:00:00"
  }
]
```

### POST `/users`

Cria usuario.

Acesso: admin.

Body:

```json
{
  "nome": "Maria Silva",
  "email": "maria@example.com",
  "senha": "senha123",
  "role": "user",
  "dias_totais": 30,
  "telefone": "(11) 99999-9999",
  "telefone_emergencia": "(11) 98888-8888",
  "telefone_emergencia_2": "(11) 97777-7777"
}
```

Resposta:

```json
{
  "id": 2,
  "nome": "Maria Silva",
  "email": "maria@example.com",
  "role": "user",
  "dias_totais": 30,
  "dias_restantes": 30,
  "criado_em": "2026-05-05T14:00:00"
}
```

### PUT `/users/{user_id}`

Edita usuario.

Acesso: admin.

Body:

```json
{
  "nome": "Maria Souza",
  "email": "maria.souza@example.com",
  "dias_totais": 25
}
```

Observacao: a rota permite alterar a senha, mas nao altera o `role`. Telefones de emergencia,
endereco e dados bancarios são retornados apenas pela rota administrativa de dados sensiveis.

### PUT `/me/configuracoes`

Edita nome/email do usuario autenticado.

Acesso: autenticado.

Body:

```json
{
  "nome": "Novo Nome",
  "email": "novo@example.com"
}
```

## Relatorios

### GET `/relatorios`

Retorna resumo por colaborador.

Acesso: admin.

Resposta:

```json
{
  "colaboradores": [
    {
      "id": 1,
      "nome": "Administrador",
      "email": "admin@sistema.com",
      "dias_totais": 30,
      "dias_usados": 15,
      "dias_restantes": 15,
      "ferias": [
        {
          "id": 1,
          "data_inicio": "2026-05-05",
          "data_fim": "2026-05-19",
          "dias_usados": 15
        }
      ]
    }
  ]
}
```

## Logs

### GET `/logs`

Lista logs do sistema.

Acesso: admin.

Resposta:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "acao": "FERIAS_REGISTRADA",
    "detalhes": "Periodo: 2026-05-05 a 2026-05-19 (15 dias)",
    "criado_em": "2026-05-05T14:00:00"
  }
]
```

## Documentos

### POST `/documentos/upload`

Envia um documento para o usuario informado.

Acesso: autenticado.

Content-Type:

```text
multipart/form-data
```

Campos:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `file` | arquivo | Sim | PDF, JPEG ou PNG de ate 10 MB |
| `tipo` | string | Sim | `atestado` ou `contracheque` |
| `user_id` | integer | Sim | Usuario dono do documento |

Observacoes:

- Usuarios comuns podem enviar apenas documentos para si mesmos.
- Apenas administradores podem enviar `contracheque`.
- Os arquivos sao salvos em pasta local configurada por `UPLOAD_DIR`.
- Contracheques enviados por administradores ficam apenas em `enviados/nome-administrador/nome-colaborador/arquivo`.
- Atestados ficam apenas em `recebidos/nome-colaborador/arquivo`, inclusive quando o remetente possui perfil administrador.
- Cada upload gera exatamente um arquivo fisico.

### GET `/documentos/historico`

Retorna os documentos em duas listas: `recebidos` e `enviados`.

Acesso: autenticado.

- Para administradores, `enviados` contem os contracheques encaminhados pelo administrador autenticado; `recebidos` contem os atestados encaminhados por colaboradores e administradores.
- Para colaboradores, `enviados` contem os proprios atestados; `recebidos` contem os documentos destinados a eles.

### GET `/documentos/{doc_id}/download`

Baixa o documento.

Acesso: admin ou usuario dono do documento.

### GET `/documentos/{doc_id}/visualizar`

Abre o documento inline quando o navegador suportar o tipo do arquivo.

Acesso: admin ou usuario dono do documento.

## Codigos de Erro Comuns

| Codigo | Significado | Situacao comum |
|---|---|---|
| `400` | Requisicao invalida | Saldo insuficiente, email duplicado, conflito de ferias |
| `401` | Nao autenticado | Token ausente, invalido ou expirado |
| `403` | Sem permissao | Usuario comum acessando rota admin |
| `404` | Nao encontrado | Ferias ou usuario inexistente |
| `422` | Erro de validacao | Body fora do formato esperado |
