import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import socket
from datetime import datetime
from threading import Thread
import json
import logging

BASE_DIR = pathlib.Path()
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000
BUFFER = 1024
dict_to_write = {}


class HTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        run_client(data=data)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        if route.path == '/':
            self.send_html_file('index.html')
        elif route.path == '/message.html':
            self.send_html_file('message.html')
        else:
            file = BASE_DIR / route.path[1:]
            if file.exists():
                self.send_static_file(file)
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static_file(self, filename):
        self.send_response(200)
        mime_type, *rest = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())


def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_address = SERVER_IP, SERVER_PORT
    sock.bind(socket_address)
    try:
        while True:
            data, address = sock.recvfrom(BUFFER)
            logging.info(f'Server: Received data: {data.decode()}: from address {address}')
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            print(data_dict)
            dict_to_write[str(datetime.now())] = data_dict
            with open('storage/data.json', 'w') as file:
                json.dump(dict_to_write, file, indent=6, ensure_ascii=False)
            logging.info(f'Send data: {data.decode()} to address: {address}')
    except KeyboardInterrupt:
        logging.info(f'Destroy Server')
    finally:
        sock.close()


def run_client(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (SERVER_IP, SERVER_PORT))
    sock.close()


def run():
    http = HTTPServer((SERVER_IP, SERVER_PORT), HTTPHandler)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")
    server = Thread(target=run_socket_server)
    client = Thread(target=run)

    server.start()
    client.start()
    server.join()
    client.join()
