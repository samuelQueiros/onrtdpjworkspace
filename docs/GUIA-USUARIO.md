# Guia do Usuario

Este guia explica como usar o Sistema de Gestao de Ferias ONRTDPJ.

## Acesso

Abra o frontend:

```text
http://127.0.0.1:5173
```

Informe email e senha.

Credencial inicial:

Solicite ao administrador responsavel o e-mail e a senha de acesso. Em ambientes Docker, esses dados sao definidos pelas variaveis `ADMIN_EMAIL` e `ADMIN_PASSWORD` no arquivo `.env`.

## Perfis

### Colaborador

Pode:

- Ver dashboard.
- Consultar seu saldo.
- Solicitar ferias.
- Cancelar suas ferias.
- Ver disponibilidade geral.
- Ver ferias marcadas por todos.

### Administrador

Pode:

- Fazer tudo que um colaborador faz.
- Cadastrar usuarios.
- Editar dados de usuarios.
- Consultar relatorios.
- Consultar logs.
- Exportar logs para Excel.

## Dashboard

O dashboard mostra:

- Dias restantes.
- Dias usados.
- Total de periodos registrados.
- Proximas ferias.
- Atalhos para solicitacao, disponibilidade e relatorios.

## Minhas Ferias

Tela para consultar os periodos de ferias do usuario logado.

Informacoes exibidas:

- Data de inicio em `DD/MM/AAAA`.
- Data de fim em `DD/MM/AAAA`.
- Quantidade de dias usados.
- Data de criacao.
- Status.

Tambem e possivel cancelar um periodo.

## Solicitar Ferias

Passos:

1. Acesse `Solicitar Ferias`.
2. Informe data de inicio.
3. Informe data de fim.
4. Confira o resumo:
   - Dias solicitados.
   - Saldo atual.
   - Saldo apos envio.
5. Clique em `Registrar ferias`.

O sistema bloqueia a solicitacao quando:

- A data final e anterior a data inicial.
- O usuario nao possui saldo suficiente.
- O periodo cruza datas bloqueadas pelo limite simultaneo.

## Disponibilidade

O calendario mostra ferias de todos os colaboradores.

Cores:

- Azul: existe ferias marcada no dia.
- Vermelho: o limite de colaboradores em ferias foi atingido.
- Sem destaque: dia livre.

Quando um dia tem ferias marcada, o numero pequeno indica quantas pessoas estao em ferias naquele dia.

Na lateral, o sistema lista:

- Nome do colaborador.
- Periodo marcado.
- Quantidade de dias.
- Periodos bloqueados por limite.

## Usuarios

Disponivel apenas para administradores.

Permite:

- Criar usuario.
- Informar nome, email, senha, perfil e dias totais.
- Editar nome, email e dias totais.

Observacao: a tela atual nao altera senha nem perfil depois da criacao.

## Relatorios

Disponivel apenas para administradores.

Mostra:

- Total de colaboradores.
- Dias totais.
- Dias usados.
- Dias disponiveis.
- Resumo por colaborador.
- Periodos registrados.

## Logs

Disponivel apenas para administradores.

Mostra eventos como:

- Usuario criado.
- Ferias registrada.
- Ferias editada.
- Ferias cancelada.

## Exportar Logs para Excel

Na tela `Logs do Sistema`, clique em:

```text
Exportar Excel
```

O sistema baixa um arquivo `.csv` que pode ser aberto no Excel.

O arquivo contem:

- Data.
- Acao.
- Usuario.
- Detalhes.

## Boas Praticas

- Antes de solicitar ferias, confira a tela de disponibilidade.
- Mantenha o saldo de dias atualizado no cadastro do usuario.
- Use os logs para auditar alteracoes importantes.
- Em ambiente real, troque a senha inicial do administrador.
