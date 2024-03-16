from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CustomUserSerializer, ReferralCodeSerializer
from .models import ReferralCode
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.utils.encoding import force_str


User = get_user_model()

class CreateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=CustomUserSerializer)
    def post(self, request, format=None):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''
        Здесь пример реализации верификации мэйла при помощи emailhunter.co
        Это пример того, как это можно реализовать в моём коде, но по причине того, чтобы зарегистрировать аккаунт необходима верификация
        при помощи номера телефона, Российские номера телефона не принимаются более, api ключ для полной реализации я получить не могу
        email = request.data.get('email')
        if email:
            # Проверка email через API Hunter.io
            response = requests.get(
                f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={settings.HUNTER_API_KEY}"
            )
            if response.status_code == 200 and response.json()['data']['status'] == "valid":
                serializer = CustomUserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Email verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        '''

''' Пример использования API Clearbit, как это может быть реализовано. 
❗API keys are available for Clearbit accounts created in 2023 and earlier. If you signed up in 2024, free or paid plans with API keys are not available.
По этой причине,я указываю пример данной реализации, так как API ключ невозможно получить в 2024
# Настройка ключа API Clearbit
clearbit.key = 'your_clearbit_api_key_here'

class RegisterUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Получение данных о пользователе от Clearbit
            email = serializer.validated_data.get('email')
            clearbit_response = clearbit.Enrichment.find(email=email, stream=True)

            # Можно использовать данные из clearbit_response для обогащения
            # информации о пользователе
            # Например:
            if clearbit_response and 'person' in clearbit_response:
                person_info = clearbit_response['person']

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
'''


class CreateReferralCodeView(CreateAPIView):

    queryset = ReferralCode.objects.all()
    serializer_class = ReferralCodeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(security=[{'Bearer': []}])
    def perform_create(self, serializer):
        # Деактивация всех реферальных кодов пользователя
        ReferralCode.objects.filter(user=self.request.user).update(is_active=False)
        # Создание нового реферального кода как активного
        serializer.save(user=self.request.user, is_active=True)


class DeleteActiveReferralCodeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(security=[{'Bearer': []}])
    def delete(self, request, *args, **kwargs):
        # Попытка найти активный реферальный код пользователя
        referral_code = ReferralCode.objects.filter(user=request.user, is_active=True).first()
        if referral_code:
            # Если активный реферальный код найден, удаляю его
            referral_code.delete()
            return Response({'message': 'Реферальный код успешно удален.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            # Если активный реферальный код не найден, возвращаю сообщение об ошибке
            return Response({'error': 'Активный реферальный код не найден.'}, status=status.HTTP_404_NOT_FOUND)


class RetrieveReferralCodeByEmail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get referral code by email",
        manual_parameters=[
            openapi.Parameter(
                name="email",
                in_=openapi.IN_QUERY,
                description="Email of the referrer",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={200: openapi.Response('Response description', ReferralCodeSerializer)},
        security=[{'Bearer': []}],
    )
    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', None)
        if email is None:
            return Response({'error': 'Необходимо указать email адрес.'}, status=400)

        # Попытка получить реферальный код из кеша
        cached_referral_code = cache.get(email)
        if cached_referral_code:
            return Response({'referral_code': cached_referral_code})

        try:
            user = User.objects.get(email=email)
            referral_code = ReferralCode.objects.filter(user=user, is_active=True).first()
            if referral_code:
                # Кеширование реферального кода
                cache.set(email, force_str(referral_code.code), timeout=3600)  # Кеширую на 1 час
                return Response({'referral_code': force_str(referral_code.code)})
            else:
                return Response({'error': 'Активный реферальный код не найден.'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким email не найден.'}, status=404)


class ReferralsListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(security=[{'Bearer': []}])
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
            referrals = user.referrals.all()
            referrals_data = CustomUserSerializer(referrals, many=True).data
            return Response(referrals_data)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=404)