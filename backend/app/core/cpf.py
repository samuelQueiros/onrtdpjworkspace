import re


def normalizar_cpf(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def validar_cpf(valor: str) -> str:
    if not isinstance(valor, str) or not re.fullmatch(r"[0-9.\-\s]+", valor):
        raise ValueError("CPF invalido")
    cpf = normalizar_cpf(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValueError("CPF invalido")

    for tamanho in (9, 10):
        soma = sum(int(cpf[indice]) * (tamanho + 1 - indice) for indice in range(tamanho))
        digito = (soma * 10) % 11
        digito = 0 if digito == 10 else digito
        if digito != int(cpf[tamanho]):
            raise ValueError("CPF invalido")
    return cpf


def formatar_cpf(valor: str) -> str:
    cpf = normalizar_cpf(valor)
    if len(cpf) != 11:
        return valor
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def mascarar_cpf(valor: str | None) -> str | None:
    if not valor:
        return None
    cpf = normalizar_cpf(valor)
    if len(cpf) != 11:
        return "***.***.***-**"
    return f"***.***.***-{cpf[-2:]}"
