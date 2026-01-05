import http.server
import ssl
import threading

# Configuration
CERT_FILE = "server.pem"
HTTPS_PORT = 443
HTTP_PORT = 80

# 1. HTTPS Handler (The Real Site)
class SecureHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>SUCCESS: T3.1 HTTPS Access Validated</h1>")
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

# 2. HTTP Redirect Handler (The Redirection)
class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.redirect()
    def do_HEAD(self):
        self.redirect()

    def redirect(self):
        # Force 301 Redirection
        new_path = "https://10.0.1.1" + self.path
        self.send_response(301)
        self.send_header('Location', new_path)
        self.end_headers()

def run_https():
    server_address = ('0.0.0.0', HTTPS_PORT)
    # Check if cert exists, if not, simplified run (or crash, but you have the cert)
    httpd = http.server.HTTPServer(server_address, SecureHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()

def run_http_redirect():
    server_address = ('0.0.0.0', HTTP_PORT)
    httpd = http.server.HTTPServer(server_address, RedirectHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    t1 = threading.Thread(target=run_https)
    t2 = threading.Thread(target=run_http_redirect)
    t1.start()
    t2.start()
