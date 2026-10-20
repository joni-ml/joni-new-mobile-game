"""
פותחים את דף הבוטים בטלפון: המחשב מגיש את הדף ברשת ה-Wi-Fi של הבית.
הטלפון צריך להיות מחובר לאותו Wi-Fi כמו המחשב.

  python live.py --phone     # מסחר חי + הדף בטלפון
  python phone.py            # רק להגיש את הדף האחרון (בלי לסחור)

בפעם הראשונה ווינדוס ישאל אם לאפשר ל-Python גישה לרשת - לוחצים "אפשר" (Allow).
רק הדף עצמו נגיש מהטלפון. ההגדרות, המצב השמור ושאר הקבצים לא נגישים.
"""

import argparse
import http.server
import os
import socket
import threading

WAITING = """<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="10">
<title>בוטי מסחר</title></head><body style="font-family:system-ui,sans-serif;padding:24px">
<p>עוד אין דף. הוא ייווצר אחרי הנר הראשון, והדף הזה יתרענן לבד.</p></body></html>"""


def local_ip():
    """הכתובת של המחשב ברשת הביתית (למשל 192.168.1.23)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))     # לא באמת שולח כלום, רק בוחר את כרטיס הרשת הנכון
        return s.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())
    finally:
        s.close()


def make_handler(page):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?")[0] not in ("/", "/index.html"):
                self.send_error(404)
                return
            body = WAITING.encode()
            if os.path.exists(page):
                with open(page, "rb") as f:
                    body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # לא להדפיס שורה על כל רענון של הטלפון
            pass
    return Handler


def serve(page, port=8000):
    """מתחיל להגיש את הדף ברקע. מחזיר את הכתובת לפתוח בטלפון."""
    for p in range(port, port + 20):    # אם הפורט תפוס, מנסים את הבא
        try:
            server = http.server.ThreadingHTTPServer(("0.0.0.0", p), make_handler(os.path.abspath(page)))
            break
        except OSError:
            continue
    else:
        raise SystemExit(f"לא מצאתי פורט פנוי בין {port} ל-{port + 19}")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://{local_ip()}:{server.server_address[1]}"


def announce(url):
    print(f"לפתוח בטלפון (מחובר לאותו Wi-Fi): {url}")
    print("המחשב צריך להישאר דלוק ולא במצב שינה.")


def main():
    p = argparse.ArgumentParser(description="מגיש את דף הבוטים לטלפון")
    p.add_argument("page", nargs="?", help="איזה דף להגיש (ברירת מחדל: live_dashboard.html, ואם אין - dashboard.html)")
    p.add_argument("--port", type=int, default=8000)
    args = p.parse_args()
    page = args.page or ("live_dashboard.html" if os.path.exists("live_dashboard.html") else "dashboard.html")
    announce(serve(page, args.port))
    print("כדי לעצור: Ctrl+C")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
