import socket
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus

HOST = '0.0.0.0'
PORT = 8080

def parse_request(request_data):
    lines = request_data.split('\r\n')
    request_line = lines[0]
    method, path, _ = request_line.split()

    headers = {}
    for line in lines[1:]:
        if not line:
            break
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key] = value

    return method, path, headers

def extract_status_code(path):
    try:
        query = urlparse(path).query
        params = parse_qs(query)
        status_value = int(params.get("status", [200])[0])
        return HTTPStatus(status_value)
    except (ValueError, KeyError):
        return HTTPStatus.OK

def handle_connection(conn, addr):
    request = conn.recv(1024).decode('utf-8')
    if not request:
        return

    method, path, headers = parse_request(request)
    status = extract_status_code(path)

    response_lines = [
        f"HTTP/1.1 {status.value} {status.phrase}",
        "Content-Type: text/plain; charset=utf-8",
        "",
        f"Request Method: {method}",
        f"Request Source: {addr}",
        f"Response Status: {status.value} {status.phrase}",
    ]
    for k, v in headers.items():
        response_lines.append(f"{k}: {v}")

    response_body = "\r\n".join(response_lines)
    conn.sendall(response_body.encode('utf-8'))

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Server running on http://{HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                handle_connection(conn, addr)

if __name__ == '__main__':
    run_server()
