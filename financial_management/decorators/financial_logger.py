import functools
import traceback

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import AuditSeverity


def financial_log(action, severity=AuditSeverity.INFO):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args else None)
            user = getattr(request, "user", None) if request else None
            ip = request.META.get("REMOTE_ADDR", "0.0.0.0") if request else "0.0.0.0"
            agent = request.META.get("HTTP_USER_AGENT", "unknown") if request else "unknown"

            try:
                result = func(*args, **kwargs)

                tx = getattr(result, "transaction", None)
                info = getattr(result, "extra_info", {})

                FinancialLogger.log(
                    user=user,
                    action=action,
                    severity=severity,
                    transaction=tx,
                    ip_address=ip,
                    user_agent=agent,
                    extra_info=info
                )

                return result

            except Exception as e:
                FinancialLogger.log(
                    user=user,
                    action=action,
                    severity=AuditSeverity.CRITICAL,
                    transaction=None,
                    ip_address=ip,
                    user_agent=agent,
                    extra_info={
                        "error": str(e),
                        "trace": traceback.format_exc()
                    }
                )
                raise
        return wrapper
    return decorator
