import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        # Здесь мы просто вызываем метод create, который уже сохраняет пользователя
        user = serializer.save()
        print(user.public_key)

        # Возвращаем данные пользователя, включая ключи
        return Response({
            'id': user.id,
            'username': user.username,
            'public_key': user.public_key,
        }, status=status.HTTP_201_CREATED)
        
class MessageView(APIView):
    def post(self, request):
        encrypted_message = request.data.get('message')
        username = request.data.get('username')  # Получаем имя пользователя из запроса
        print('Сообщение от пользователя: ', encrypted_message)

        # Попытка найти пользователя по имени
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound('Пользователь не найден.')

        # Декодируем сообщение из latin1
        encrypted_message_bytes = encrypted_message.encode('latin1')
        
        

        # Загружаем приватный ключ
        private_key = serialization.load_pem_private_key(
            user.private_key.encode(),
            password=None,
            backend=default_backend()
        )

        # Расшифровка сообщения
        decrypted_message = private_key.decrypt(
            encrypted_message_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        

        return Response({'message': decrypted_message.decode()})