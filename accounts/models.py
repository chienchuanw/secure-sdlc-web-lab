from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class PasswordResetToken(models.Model):
    """
    密碼重設 Token 模型

    ⚠️ 安全問題（刻意引入）：
    1. Token 使用弱隨機數產生（可預測）
    2. 沒有過期時間檢查
    3. Token 可以重複使用（沒有 is_used 欄位的檢查）
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name='使用者'
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='重設 Token'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='建立時間'
    )

    is_used = models.BooleanField(
        default=False,
        verbose_name='是否已使用'
    )

    class Meta:
        verbose_name = '密碼重設 Token'
        verbose_name_plural = '密碼重設 Tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."

    @staticmethod
    def generate_weak_token():
        """
        產生弱 Token（刻意使用弱隨機數）

        ⚠️ 漏洞：使用 random 而非 secrets
        - random 是偽隨機數產生器（PRNG），可預測
        - 正確做法應該使用 secrets.token_urlsafe()
        """
        # 🔴 弱隨機數產生
        # 正確做法：secrets.token_urlsafe(32)
        length = 32
        characters = string.ascii_letters + string.digits
        weak_token = ''.join(random.choice(characters) for _ in range(length))
        return weak_token

    def is_expired(self):
        """
        檢查 token 是否過期

        ⚠️ 漏洞：這個方法存在但從未被呼叫
        - Token 永遠不會過期
        - 攻擊者可以無限期使用竊取的 token
        """
        from datetime import timedelta
        expiry_time = timedelta(hours=24)
        return timezone.now() > self.created_at + expiry_time

    def mark_as_used(self):
        """
        標記 token 為已使用

        ⚠️ 漏洞：這個方法存在但從未被呼叫
        - Token 可以重複使用
        - 攻擊者可以多次使用同一個 token
        """
        self.is_used = True
        self.save()
