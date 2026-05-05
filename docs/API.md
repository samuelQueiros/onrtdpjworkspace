# Documentacao da API

Base URL local:

```text
http://127.0.0.1:8000
```

Documentacao interativa:

```text
http://127.0.0.1:8000/docs
```

## Autenticacao

As rotas protegidas exigem header:

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

Realiza login.

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
  -Uri http://127.0.0.1:8000/auth/login `
  -Body @{username='admin@sistema.com';password='admin123'}
```

Resposta:

```json
{
  "access_token": "jwt",
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
  "dias_totais": 30
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

Observacao: a rota atual nao altera `role` nem senha.

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

## Codigos de Erro Comuns

| Codigo | Significado | Situacao comum |
|---|---|---|
| `400` | Requisicao invalida | Saldo insuficiente, email duplicado, conflito de ferias |
| `401` | Nao autenticado | Token ausente, invalido ou expirado |
| `403` | Sem permissao | Usuario comum acessando rota admin |
| `404` | Nao encontrado | Ferias ou usuario inexistente |
| `422` | Erro de validacao | Body fora do formato esperado |
