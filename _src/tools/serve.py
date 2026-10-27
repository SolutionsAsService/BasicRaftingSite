"""Serve the built site on an ephemeral local port, for tools that need http://.

The pages use root-absolute paths (/assets/css/styles.css), which resolve to the
drive root under file:// and silently drop the stylesheet. Measuring a file://
page therefore measures an unstyled one. Always measure over http.
"""
import functools
import http.server
import socketserver
import threading
from contextlib import contextmanager

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]


@contextmanager
def serve():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass

    handler = functools.partial(Handler, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        t.join(timeout=2)
