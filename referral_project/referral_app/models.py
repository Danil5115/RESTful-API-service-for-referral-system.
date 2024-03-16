from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

## Модель пользователя
class CustomUser(AbstractUser):
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')


## Модель реферального кода
class ReferralCode(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referral_codes')
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"
