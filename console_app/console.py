import requests
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# URL вашего сервера
BASE_URL = 'http://localhost:8000/api/users/'

def register_user(username):
    response = requests.post(f'{BASE_URL}register/', json={'username': username})
    if response.status_code == 201:
        print(f'Пользователь {username} зарегистрирован.')
        print(response.json())
        return response.json()
    else:
        print('Ошибка регистрации:', response.json())
        return None

def encrypt_message(public_key_pem, message):
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )
    encrypted_message = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_message).decode('utf-8')

def send_message(username, encrypted_message):
    encrypted_message_bytes = base64.b64decode(encrypted_message)
    response = requests.post(f'{BASE_URL}message/', json={
        'username': username,
        'message': encrypted_message_bytes.decode('latin1')})
    if response.status_code == 200:
        print('Ответ от сервера:', response.json()['message'])
    else:
        print('Ошибка отправки сообщения:', response.json())

def main():
    # Регистрация пользователя
    username = input('Введите имя пользователя: ')
    user_data = register_user(username)

    if not user_data:
        print("Регистрация не удалась. Завершение программы.")
        return

    # Получение публичного ключа пользователя
    public_key = user_data['public_key']

    # Цикл для отправки сообщений
    while True:
        # Ввод сообщения
        message = input('Введите сообщение для отправки (или "exit" для выхода): ')
        
        # Проверка на выход
        if message.lower() in ['exit', 'quit']:
            print("Завершение работы клиента.")
            break

        # Шифрование и отправка сообщения
        encrypted_message = encrypt_message(public_key, message)
        print('Зашифрованное сообщение:', encrypted_message)
        send_message(username, encrypted_message)

if __name__ == '__main__':
    main()