import argparse, logging, signal, threading
from .engine import run_once, deliver_notifications

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s worker %(message)s')
    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_:stop.set())
    signal.signal(signal.SIGTERM, lambda *_:stop.set())
    while not stop.is_set():
        run_once()
        deliver_notifications()
        if args.once: break
        stop.wait(2)

if __name__ == '__main__': main()
