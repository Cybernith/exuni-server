from django.utils.timezone import now

from financial_management.models import FinancialAuditLog, AuditSeverity


class FinancialLogger:
    @staticmethod
    def log(
        user,
        action,
        severity=AuditSeverity.INFO,
        transaction=None,
        ip_address=None,
        user_agent=None,
        extra_info=None,
        receiver=None
    ):
        FinancialAuditLog.objects.create(
            user=user,
            transaction=transaction,
            action=action,
            severity=severity,
            ip_address=ip_address or "0.0.0.0",
            user_agent=user_agent or "unknown",
            extra_info=extra_info or {},
            created_at=now(),
            receiver=receiver
        )
