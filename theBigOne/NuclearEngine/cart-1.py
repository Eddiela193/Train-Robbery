#!/usr/bin/env python3
"""
Animated training TCP server with prerun of eng.py.

Behavior:
- Run "python3 -u eng.py" once at startup, capture its stdout/stderr.
- For each client that connects, immediately send the captured eng.py output
  (if any), then continue with the banner/refresh loop and payload handling.
- If a client submits the correct input, server replies "You got it!" and
  the server requests shutdown.
"""

import socket
import threading
import argparse
import sys
import time
from typing import Tuple
import subprocess

BUFFER_SIZE = 380
DEFAULT_PORT = 100

lock = threading.Lock()
stats = {
    "total_requests": 0,
    "segfault_responses": 0,
    "ok_responses": 0,
    "other_responses": 0,
}

# Banner text sent repeatedly while waiting for input
BANNER = (
    "========================================\n"
    "   THE VAULT - TRAINING CART (REFRESH)\n"
    "   Enter four CSV fields like: f1,f2,f3_hex,f4\n"
    "   (or send any single string to get echoed)\n"
    "========================================\n\n"
)

REFRESH_INTERVAL = 1.2  # seconds between banner refreshes

# captured output from eng.py (filled at startup)
ENG_OUTPUT = b""

def capture_eng_output(cmd="python3 -u eng.py"):
    """
    Run the given command with popen() and capture all stdout/stderr into a bytes buffer.
    Returns bytes (possibly empty) or None on error.
    """
    try:
        # Use subprocess to capture both stdout and stderr
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out_chunks = []
        # read until EOF
        while True:
            chunk = proc.stdout.read(1024)
            if not chunk:
                break
            out_chunks.append(chunk)
        proc.wait()
        return b"".join(out_chunks)
    except Exception as e:
        print(f"[!] Failed to capture eng.py output: {e}")
        return None

def process_payload(text: str) -> Tuple[bytes, bool]:
    """
    Process decoded text and return (response_bytes, success_bool).
    """
    parts = [p.strip() for p in text.split(",")]
    response_parts = []
    success_flag = True

    if len(parts) == 4:
        try:
            f1 = int(parts[0], 0)
            f2 = int(parts[1], 0)
            f3 = int(parts[2], 0)
            f4 = int(parts[3], 0)
            parsed_ok = True
        except Exception:
            parsed_ok = False

        if parsed_ok:
            if f1 != 332 and f1 != 328:
                response_parts.append("Item \\x90 not recognized!")
                success_flag = False
            if f2 < 8:
                response_parts.append("Completing ledger")
                success_flag = False
            if (f3 & 0xFFFFFFFF) != 0xFFFFE000:
                response_parts.append("Unrecognized return")
                success_flag = False
            if f4 > 10000:
                response_parts.append("Stack out of bounds...address too high")
                success_flag = False
            if f4 < 8000:
                response_parts.append("Stack out of bounds...unmapped address space")
                success_flag = False

            if success_flag:
                with lock:
                    stats["ok_responses"] += 1
                    stats["total_requests"] += 1
                return (b"You got it!\n", True)
            else:
                with lock:
                    stats["other_responses"] += 1
                    stats["total_requests"] += 1
                return ("\n".join(response_parts) + "\n").encode("utf-8"), False
        else:
            with lock:
                stats["other_responses"] += 1
                stats["total_requests"] += 1
            return f"You sent: {text}\n".encode("utf-8"), False
    else:
        with lock:
            stats["other_responses"] += 1
            stats["total_requests"] += 1
        return f"You sent: {text}\n".encode("utf-8"), False

def banner_sender(conn: socket.socket, stop_evt: threading.Event):
    """
    Periodically send the banner to conn until stop_evt is set.
    """
    try:
        while not stop_evt.is_set():
            try:
                conn.sendall(BANNER.encode("utf-8"))
            except Exception:
                stop_evt.set()
                return
            slept = 0.0
            while slept < REFRESH_INTERVAL and not stop_evt.is_set():
                time.sleep(0.1)
                slept += 0.1
    except Exception:
        stop_evt.set()

def handle_client(conn: socket.socket, addr, server_shutdown_evt: threading.Event):
    """
    Handle a single client connection.
    Sends ENG_OUTPUT first (if present), then runs the interactive banner + payload loop.
    """
    with conn:
        try:
            # Send eng.py captured output first (if any)
            global ENG_OUTPUT
            if ENG_OUTPUT:
                try:
                    conn.sendall(ENG_OUTPUT)
                except Exception:
                    # client closed early
                    return

            # Interactive loop: banner, read input, process, repeat until success or disconnect
            while True:
                stop_banner = threading.Event()
                bthr = threading.Thread(target=banner_sender, args=(conn, stop_banner), daemon=True)
                bthr.start()

                # prompt
                try:
                    conn.sendall(b"Type input and press Enter:\n")
                except Exception:
                    stop_banner.set()
                    bthr.join(timeout=1.0)
                    return

                received = b""
                while True:
                    try:
                        chunk = conn.recv(1024)
                    except ConnectionResetError:
                        stop_banner.set()
                        bthr.join(timeout=1.0)
                        return
                    except Exception:
                        stop_banner.set()
                        bthr.join(timeout=1.0)
                        return

                    if not chunk:
                        stop_banner.set()
                        bthr.join(timeout=1.0)
                        return

                    received += chunk
                    if b"\n" in received or b"\r" in received:
                        break
                    if len(received) >= BUFFER_SIZE:
                        break

                stop_banner.set()
                bthr.join(timeout=1.0)

                if len(received) >= BUFFER_SIZE:
                    try:
                        conn.sendall(b"Segmentation Fault\n")
                    except Exception:
                        return
                    with lock:
                        stats["segfault_responses"] += 1
                        stats["total_requests"] += 1
                    continue

                try:
                    text = received.decode("utf-8", errors="replace").strip()
                except Exception:
                    text = "<decode error>"

                resp_bytes, success = process_payload(text)
                try:
                    conn.sendall(resp_bytes)
                except Exception:
                    return

                if success:
                    server_shutdown_evt.set()
                    return
                else:
                    continue

        except Exception as e:
            print(f"[!] Exception while handling client {addr}: {e}")
            return

def run_server(host: str, port: int):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)
    print(f"[+] Listening on {host}:{port}  (CTRL-C to stop)")

    server_shutdown_evt = threading.Event()
    threads = []

    try:
        while not server_shutdown_evt.is_set():
            try:
                server_sock.settimeout(1.0)
                conn, addr = server_sock.accept()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[!] accept() error: {e}")
                break

            print(f"[+] Client connected from {addr}")
            t = threading.Thread(target=handle_client, args=(conn, addr, server_shutdown_evt), daemon=True)
            threads.append(t)
            t.start()

        print("[*] Shutdown requested — waiting for client handlers to finish...")
        for t in threads:
            t.join(timeout=2.0)

    except KeyboardInterrupt:
        print("\n[+] Server interrupted by user (CTRL-C)")

    finally:
        server_sock.close()
        dump_stats()

def dump_stats():
    with lock:
        total = stats["total_requests"]
        print(f"  Total requests processed: {total}")
        print(f"  OK ('You got it!') responses: {stats['ok_responses']}")
        print(f"  Segmentation-Fault responses: {stats['segfault_responses']}")
        print(f"  Other responses: {stats['other_responses']}")

def simulate_virtual_clients(num_clients: int, duration: int, ramp: float = 0.0):
    print(f"[+] Starting fake-DDoS simulation: {num_clients} virtual requests over {duration}s...")
    start = time.time()
    threads = []

    def worker(payload: bytes):
        process_payload(payload)

    import random
    def random_payload(i):
        r = random.random()
        if r < 0.05:
            return b"A" * BUFFER_SIZE
        elif r < 0.6:
            f1 = random.choice([332, 328, 999])
            f2 = random.randint(0, 12000)
            f3 = random.choice([0xFFFFE000, random.randint(0, 0xFFFFFFFF)])
            f4 = random.randint(7000, 11000)
            return f"{f1},{f2},{hex(f3)},{f4}\n".encode('utf-8')
        else:
            return f"HELLO-{i}".encode('utf-8')

    for i in range(num_clients):
        payload = random_payload(i)
        t = threading.Thread(target=worker, args=(payload,), daemon=True)
        threads.append(t)
        t.start()
        if duration > 0:
            time.sleep(duration / max(1, num_clients))

    for t in threads:
        t.join(timeout=1.0)
    end = time.time()
    print(f"[+] Simulation finished in {end - start:.2f}s")
    dump_stats()

def main():
    global ENG_OUTPUT
    parser = argparse.ArgumentParser(description="Animated training TCP server (eng.py prerun)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to bind (default {DEFAULT_PORT}). Ports <1024 require elevated privileges.")
    parser.add_argument("--simulate", action="store_true",
                        help="Run internal fake-DDoS simulation (no real network traffic)")
    parser.add_argument("--virtual-clients", type=int, default=200,
                        help="Number of virtual clients for simulation (default 200)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Duration in seconds to spread the virtual requests (default 5)")
    args = parser.parse_args()

    if args.simulate:
        with lock:
            stats.update({k: 0 for k in stats})
        simulate_virtual_clients(args.virtual_clients, args.duration)
        return

    # Capture eng.py output once at startup
    print("[*] Running eng.py once and capturing output...")
    captured = capture_eng_output("python3 -u eng.py")
    if captured is None:
        print("[!] eng.py capture failed; continuing without eng output.")
        ENG_OUTPUT = b""
    else:
        ENG_OUTPUT = captured
        print(f"[*] Captured {len(ENG_OUTPUT)} bytes from eng.py")

    if args.port < 1024:
        print("[!] Note: ports <1024 are privileged. You may need to run this with elevated privileges.")
        print("    Only run with elevated privileges on machines you own or in a lab environment!\n")

    try:
        run_server(args.host, args.port)
    except PermissionError:
        print("[ERROR] Permission denied when binding to port. Try a non-privileged port (>=1024) or run as root.")
    except OSError as e:
        print(f"[ERROR] OS error: {e}")

if __name__ == "__main__":
    main()
