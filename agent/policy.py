from agent.config import settings


def should_require_approval(risk_tags: list[str]) -> bool:
    return any(tag in settings.risk_require_confirmation for tag in risk_tags)
