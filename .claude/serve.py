#!/usr/bin/env python3
"""Static server for the portfolio.

`python3 -m http.server` is not usable here: its module-level argparse setup
calls os.getcwd(), which the sandbox denies before any argument is read. This
does the same job with the directory pinned to the repo root instead.
"""
import functools
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4321


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # never cache during development, or an edit needs a hard reload
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    handler = functools.partial(Handler, directory=ROOT)
    print("serving %s on http://127.0.0.1:%d" % (ROOT, PORT), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()
