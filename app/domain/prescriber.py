from app.domain.provider import Provider, ProviderId

# Prescriber is a domain-language alias for Provider in the current model.
Prescriber = Provider
PrescriberId = ProviderId

__all__ = ["Prescriber", "PrescriberId"]
