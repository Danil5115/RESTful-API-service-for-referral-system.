# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import ReferralCode
from django.utils import timezone

CustomUser = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'referral_code')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        referral_code_str = validated_data.pop('referral_code', None)
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if referral_code_str:
            try:
                referral_code = ReferralCode.objects.get(code=referral_code_str, is_active=True)
                user.referrer = referral_code.user
                user.save()
            except ReferralCode.DoesNotExist:
                pass

        return user


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ('code', 'expires_at', 'is_active', 'user')
        read_only_fields = ('code', 'user')

    def validate_expires_at(self, value):
        # Проверка, что expires_at не раньше текущей даты
        if value < timezone.now():
            raise serializers.ValidationError("Срок действия реферального кода не может быть в прошлом.")
        return value
