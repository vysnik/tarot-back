# Стандартные библиотеки
import requests

# Внешние библиотеки
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests

# Django/DRF
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

import logging
logger = logging.getLogger(__name__)



User = get_user_model()


ALLOWED_GOOGLE_CLIENT_IDS = [
    # iOS
    "225071427166-3dbnmc3iuc7vkcfbsgl55c306vuv7a8d.apps.googleusercontent.com",
    # Web
    "225071427166-i0dfmku2lk64724jc393mudd4gpdm4ja.apps.googleusercontent.com",
]

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        try:
            # ❶ НЕ передаём audience → библиотека проверит только подпись/exp/iat
            idinfo = id_token.verify_oauth2_token(
                token,
                g_requests.Request(),
                clock_skew_in_seconds=10,   # допускаем ±10 сек
            )

            # ❷ Проверяем aud вручную
            if idinfo["aud"] not in ALLOWED_GOOGLE_CLIENT_IDS:
                return Response({"error": "Wrong audience"}, status=400)

            email = idinfo["email"]
            name  = idinfo.get("name", "")

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"username": email, "first_name": name},
            )

            refresh = RefreshToken.for_user(user)
            return Response({"refresh": str(refresh),
                             "access":  str(refresh.access_token)})
        except ValueError as e:
            logger.exception("Google token verification failed")
            return Response({"error": str(e)}, status=400)


class AppleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        try:
            # Получаем публичные ключи Apple
            apple_keys = requests.get("https://appleid.apple.com/auth/keys").json()["keys"]

            # Декодируем без верификации, чтобы узнать `kid` и `alg`
            unverified_header = jwt.get_unverified_header(token)

            # Ищем подходящий ключ
            key = next(k for k in apple_keys if k["kid"] == unverified_header["kid"])

            # Верификация токена
            decoded = jwt.decode(
                token,
                key,
                algorithms=unverified_header["alg"],
                audience="com.your.bundle.id",  # <- замени на свой Apple client_id (bundle ID)
                issuer="https://appleid.apple.com"
            )

            email = decoded.get("email")
            sub = decoded.get("sub")

            if not email:
                return Response({"error": "Apple token missing email"}, status=400)

            user, _ = User.objects.get_or_create(email=email, defaults={
                "username": email.split("@")[0],
                "first_name": "",
            })

            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        except Exception as e:
            return Response({"error": "Invalid Apple token", "details": str(e)}, status=400)