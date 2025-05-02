from django.db import models


class ChatMessage(models.Model):
    USER = 'user'
    ASSISTANT = 'assistant'

    ROLES = (
        (USER, 'کاربر'),
        (ASSISTANT, 'دستیار'),
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=9, choices=ROLES, default=USER)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class TokenUsage(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='token_usages')
    model_name = models.CharField(max_length=50)
    tokens_used = models.PositiveIntegerField()
    cost_usd = models.DecimalField(max_digits=10, decimal_places=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user} - {self.tokens_used}"
