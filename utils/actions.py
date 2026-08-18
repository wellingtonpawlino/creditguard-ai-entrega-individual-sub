import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def notificar_crm(inputs: dict, probability: float) -> bool:
    """BAIXO RISCO: dispara webhook ao CRM/ERP com resultado de aprovação."""
    webhook_url = os.environ.get("CRM_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("CRM_WEBHOOK_URL não configurada — notificação omitida.")
        return False
    try:
        import httpx
        resp = httpx.post(
            webhook_url,
            json={
                "event": "credit_approved",
                "risk_level": "BAIXO RISCO",
                "probability": round(probability, 4),
                "approved": True,
                "amt_income_total": inputs.get("AMT_INCOME_TOTAL"),
                "amt_credit": inputs.get("AMT_CREDIT"),
            },
            timeout=5,
        )
        logger.info(f"CRM webhook: status={resp.status_code}")
        return resp.status_code < 300
    except Exception as e:
        logger.error(f"Falha no webhook CRM: {e}")
        return False


def gerar_parecer_agente(inputs: dict, probability: float) -> str:
    """MÉDIO RISCO: aciona agente de IA (Claude) para análise complementar."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "Agente de IA indisponível — ANTHROPIC_API_KEY não configurada.\n"
            "Configure a variável de ambiente para habilitar a análise complementar."
        )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Você é um analista de crédito sênior. Avalie o perfil abaixo e emita um parecer estruturado.

Dados do cliente:
- Renda anual: R$ {inputs.get('AMT_INCOME_TOTAL', 0):,.0f}
- Crédito solicitado: R$ {inputs.get('AMT_CREDIT', 0):,.0f}
- Filhos dependentes: {inputs.get('CNT_CHILDREN', 0)}
- Score bureau 1 (EXT_SOURCE_1): {inputs.get('EXT_SOURCE_1', 'N/D')}
- Score bureau 2 (EXT_SOURCE_2): {inputs.get('EXT_SOURCE_2', 'N/D')}
- Score bureau 3 (EXT_SOURCE_3): {inputs.get('EXT_SOURCE_3', 'N/D')}
- Probabilidade de inadimplência (LightGBM): {probability:.1%}

O modelo classificou este cliente como MÉDIO RISCO (30%–70% de inadimplência).

Forneça um parecer com exatamente três seções:
1. Fatores de risco: identifique os principais fatores que elevam o risco.
2. Recomendação: aprovar, negar ou sugerir limite alternativo (com valor sugerido se aplicável).
3. Justificativa regulatória: uma frase adequada para registro em conformidade com CMN 4.966."""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Falha no agente de IA: {e}")
        return f"Erro na consulta ao agente de IA: {e}"


def notificar_analista(inputs: dict, probability: float) -> bool:
    """ALTO RISCO: notifica analista via Slack webhook ou SMTP."""
    slack_url = os.environ.get("SLACK_WEBHOOK_URL")
    if slack_url:
        return _notificar_slack(slack_url, inputs, probability)
    smtp_host = os.environ.get("SMTP_HOST")
    if smtp_host:
        return _notificar_email(smtp_host, inputs, probability)
    logger.warning(
        "Nenhum canal de notificação configurado "
        "(SLACK_WEBHOOK_URL ou SMTP_HOST ausentes)."
    )
    return False


def _notificar_slack(webhook_url: str, inputs: dict, probability: float) -> bool:
    try:
        import httpx
        texto = (
            f"🔴 *[CreditGuard AI] ALTO RISCO detectado*\n"
            f"Probabilidade de inadimplência: *{probability:.1%}*\n"
            f"Renda anual: R$ {inputs.get('AMT_INCOME_TOTAL', 0):,.0f} | "
            f"Crédito: R$ {inputs.get('AMT_CREDIT', 0):,.0f}\n"
            f"EXT_SOURCE_2: {inputs.get('EXT_SOURCE_2', 'N/D')} | "
            f"EXT_SOURCE_3: {inputs.get('EXT_SOURCE_3', 'N/D')}\n"
            f"Acesse o painel para revisão: http://localhost:8501"
        )
        resp = httpx.post(webhook_url, json={"text": texto}, timeout=5)
        logger.info(f"Slack webhook: status={resp.status_code}")
        return resp.status_code < 300
    except Exception as e:
        logger.error(f"Falha na notificação Slack: {e}")
        return False


def _notificar_email(smtp_host: str, inputs: dict, probability: float) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = f"[CreditGuard] ALTO RISCO — {probability:.1%} de inadimplência"
        msg["From"] = os.environ.get("SMTP_FROM", "creditguard@local")
        msg["To"] = os.environ.get("ANALISTA_EMAIL", "analista@local")
        msg.set_content(
            f"Cliente com risco elevado detectado pelo CreditGuard AI.\n\n"
            f"Probabilidade de inadimplência: {probability:.1%}\n"
            f"Renda anual: R$ {inputs.get('AMT_INCOME_TOTAL', 0):,.0f}\n"
            f"Crédito solicitado: R$ {inputs.get('AMT_CREDIT', 0):,.0f}\n"
            f"EXT_SOURCE_2: {inputs.get('EXT_SOURCE_2', 'N/D')}\n"
            f"EXT_SOURCE_3: {inputs.get('EXT_SOURCE_3', 'N/D')}\n\n"
            f"Acesse o painel para revisão manual: http://localhost:8501"
        )
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.send_message(msg)
        logger.info("E-mail de alto risco enviado.")
        return True
    except Exception as e:
        logger.error(f"Falha no envio de e-mail: {e}")
        return False
