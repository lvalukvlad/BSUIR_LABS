from socket import *
import sys
import os
import datetime
from urllib.parse import urlparse

def check_cache_freshness(cache_file_path):
    if not os.path.exists(cache_file_path):
        return False
    time_passed = datetime.datetime.now().timestamp() - os.path.getmtime(cache_file_path)
    return time_passed < 120


if len(sys.argv) <= 1:
    print('Запустите программу так: "python ProxyServer.py адрес_сервера"\n[адрес_сервера – IP-адрес прокси-сервера]')
    sys.exit(1)

main_socket = socket(AF_INET, SOCK_STREAM)
main_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
main_socket.bind((sys.argv[1], 8080))
main_socket.listen(10)

while True:
    print('Ожидаем подключения клиента...')
    client_connection, client_address = main_socket.accept()
    print('Подключен клиент:', client_address)

    try:
        client_request = client_connection.recv(8192).decode()
        print(client_request)

        if not client_request:
            raise RuntimeError("Получен пустой запрос")

        requested_url = client_request.split()[1]
        parsed_url = urlparse(requested_url)

        if not parsed_url.netloc:
            raise RuntimeError("Некорректный формат URL")

        target_host = parsed_url.netloc
        target_path = parsed_url.path if parsed_url.path else "/"

        cache_file_name = target_host + target_path.replace("/", "|")
        full_cache_path = cache_file_name

        if check_cache_freshness(full_cache_path):
            with open(full_cache_path, "rb") as cache_file:
                cached_content = cache_file.read()

            client_connection.send(b"HTTP/1.0 200 OK\r\n")
            client_connection.send(b"Content-Type: text/html\r\n\r\n")
            client_connection.send(cached_content)

            print("Данные получены из кэша:", full_cache_path)

        else:
            if os.path.exists(full_cache_path):
                os.remove(full_cache_path)
                print("Устаревший кэш удалён")

            target_socket = socket(AF_INET, SOCK_STREAM)
            print("Устанавливаем соединение с сервером:", target_host)

            try:
                target_socket.connect((target_host, 80))

                http_request = f"GET {target_path} HTTP/1.0\r\nHost: {target_host}\r\n\r\n"
                target_socket.send(http_request.encode())

                server_response = b""
                while True:
                    chunk = target_socket.recv(8192)
                    if not chunk:
                        break
                    server_response += chunk

                with open(full_cache_path, "wb") as new_cache_file:
                    new_cache_file.write(server_response)

                client_connection.send(server_response)
                print("Данные сохранены в кэш:", full_cache_path)

            except Exception as err:
                print("Проблема с подключением:", err)
                client_connection.send(b"HTTP/1.0 502 Bad Gateway\r\n\r\n")

            finally:
                target_socket.close()

    except RuntimeError as err:
        print("Ошибка в запросе:", err)
        client_connection.send(b"HTTP/1.0 400 Bad Request\r\n\r\n")

    except Exception as err:
        print("Непредвиденная ошибка:", err)
        client_connection.send(b"HTTP/1.0 500 Internal Server Error\r\n\r\n")

    finally:
        client_connection.close()
