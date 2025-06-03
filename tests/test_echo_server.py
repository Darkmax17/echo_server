import socket
import threading
import time
import pytest

from echo_server.server import run_server



HOST = '127.0.0.1'
PORT = 8080

@pytest.fixture(scope="module", autouse=True)
def start_server():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Wait for server to start

def send_request(request_text):
    with socket.create_connection((HOST, PORT)) as sock:
        sock.sendall(request_text.encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
    return response

def test_simple_get():
    request = "GET / HTTP/1.1\r\nHost: localhost\r\nX-Test: True\r\n\r\n"
    response = send_request(request)
    assert "Request Method: GET" in response
    assert "X-Test: True" in response
    assert "Response Status: 200 OK" in response

def test_custom_status():
    request = "GET /?status=404 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_request(request)
    assert "404 Not Found" in response

def test_invalid_status():
    request = "GET /?status=999 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_request(request)
    assert "200 OK" in response
