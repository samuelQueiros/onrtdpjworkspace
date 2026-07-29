from datetime import date, datetime
from zoneinfo import ZoneInfo


FUSO_SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def hoje_sao_paulo() -> date:
    return datetime.now(FUSO_SAO_PAULO).date()
