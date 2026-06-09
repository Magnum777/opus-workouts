
import sys, os, signal, threading, time
sys.path.insert(0, r"C:\Users\compj\.openclaw\workspace\trading-bot")
os.chdir(r"C:\Users\compj\.openclaw\workspace\trading-bot")

done = threading.Event()
lines = []

def capture():
    old = sys.stdout
    import io
    buf = io.StringIO()
    sys.stdout = buf
    try:
        import daemon
        daemon
    except Exception as e:
        print(f"DAEMON IMPORT FAILED: {e}")
    finally:
        sys.stdout = old
        lines.extend(buf.getvalue().split("\n"))
        done.set()

t = threading.Thread(target=capture, daemon=True)
t.start()
if not done.wait(timeout=150):
    print("[TIMEOUT after 150s]")
print("\n".join(lines))
