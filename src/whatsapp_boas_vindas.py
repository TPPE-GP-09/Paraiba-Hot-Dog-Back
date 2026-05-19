import logging
import re

import requests

from src.config import settings

logger = logging.getLogger(__name__)


def _formatar_telefone_whatsapp(telefone: str) -> str:
    numeros = re.sub(r"\D", "", str(telefone or ""))
    if numeros.startswith("55"):
        return numeros
    return f"55{numeros}"


def _credenciais_configuradas() -> bool:
    if not settings.whatsapp_token or not settings.phone_number_id:
        return False
    if settings.whatsapp_token == "SEU_ACCESS_TOKEN_AQUI":
        return False
    if settings.phone_number_id == "SEU_PHONE_NUMBER_ID_AQUI":
        return False
    return True


def enviar_boas_vindas(nome: str, telefone: str) -> dict:
    logger.warning(
        "Iniciando envio de WhatsApp para cliente=%s telefone=%s",
        nome,
        telefone,
    )
    if not _credenciais_configuradas():
        logger.warning(
            "Envio WhatsApp ignorado: credenciais ausentes para cliente=%s telefone=%s",
            nome,
            telefone,
        )
        return {"status": "skipped", "reason": "missing_whatsapp_credentials"}

    telefone_formatado = _formatar_telefone_whatsapp(telefone)
    api_url = f"https://graph.facebook.com/v19.0/{settings.phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone_formatado,
        "type": "text",
        "text": {
            "body": (
                f"Ola, {nome}!\n\n"
                "Seja bem-vindo ao nosso programa de fidelidade!\n\n"
                "A partir de agora voce acumula pontos a cada compra e pode trocar por recompensas incriveis.\n\n"
                "Qualquer duvida, e so nos chamar aqui."
            )
        },
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(
                "Mensagem de boas-vindas enviada com sucesso para cliente=%s telefone=%s",
                nome,
                telefone_formatado,
            )
        else:
            logger.error(
                "Falha ao enviar WhatsApp para cliente=%s telefone=%s status=%s body=%s",
                nome,
                telefone_formatado,
                response.status_code,
                response.text,
            )
        return response.json()
    except requests.RequestException as exc:
        logger.exception(
            "Erro de rede no envio de WhatsApp para cliente=%s telefone=%s: %s",
            nome,
            telefone_formatado,
            exc,
        )
        return {"status": "error", "reason": "request_exception"}
    except Exception as exc:  # pragma: no cover - defensivo para diagnostico em runtime
        logger.exception(
            "Erro inesperado no envio de WhatsApp para cliente=%s telefone=%s: %s",
            nome,
            telefone_formatado,
            exc,
        )
        return {"status": "error", "reason": "unexpected_exception"}
