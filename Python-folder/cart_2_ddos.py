#!/usr/bin/env python3

import socket
import threading
import argparse
import sys
import time
from typing import Tuple

BUFFER_SIZE = 380
DEFAULT_PORT = 100

lock = threading.Lock()
stats = {
    "total_requests": 0,
    "segfault_responses": 0,
    "ok_responses": 0,
    "other_responses": 0,
}

def process_payload(payload: bytes) -> bytes:
    """
    Recreate the C program's behavior:
    - If payload length == BUFFER_SIZE -> send "Segmentation Fault\n" and drain (simulated)
    - Else parse CSV "f1,f2,f3_hex,f4" and respond accordingly
    - Else echo "You sent: ...\n"
    """
    if len(payload) >= BUFFER_SIZE:
        with lock:
            stats["segfault_responses"] += 1
            stats["total_requests"] += 1
        return b"Segmentation Fault\n"

    # ensure text
    try:
        text = payload.decode('utf-8', errors='replace').strip()
    except Exception:
        text = "<unable to decode>"
    # try parse "d,d,hex,d"
    parts = [p.strip() for p in text.split(",")]
    response_parts = []
    success_flag = True

    if len(parts) == 4:
        # try convert parts
        try:
            f1 = int(parts[0], 0)
            f2 = int(parts[1], 0)
            # allow hex like 0xffffe000 or without 0x prefix
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
            # ensure unsigned 32 match like 0xFFFFE000
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
                return b"You got it!\n"
            else:
                with lock:
                    stats["other_responses"] += 1
                    stats["total_requests"] += 1
                return ("\n".join(response_parts) + "\n").encode('utf-8')
        else:
            # couldn't parse
            with lock:
                stats["other_responses"] += 1
                stats["total_requests"] += 1
            return f"You sent: {text}\n".encode('utf-8')
    else:
        # not 4 fields -> echo
        with lock:
            stats["other_responses"] += 1
            stats["total_requests"] += 1
        return f"You sent: {text}\n".encode('utf-8')

def handle_client(conn: socket.socket, addr: Tuple[str,int]):
    """
    Handle a single client connection (threaded).
    """
    with conn:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                return
            # If client sent exactly BUFFER_SIZE bytes, behave accordingly
            resp = process_payload(data)
            conn.sendall(resp)
        except Exception as e:
            # For educational clarity, show exception but don't expose details to external clients
            # (we only print server-side)
            print(f"[!] Exception handling {addr}: {e}")

def run_server(host: str, port: int):
    """
    Run a simple threaded TCP server that accepts connections and processes them.
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)
    print(f"[+] Listening on {host}:{port}  (CTRL-C to stop)")
    try:
        while True:
            conn, addr = server_sock.accept()
            print(f"[+] Client connected from {addr}")
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[+] Server shutting down (clean). Summary stats:")
        dump_stats()
    finally:
        server_sock.close()

def dump_stats():
    with lock:
        total = stats["total_requests"]
        print(f"  Total requests processed: {total}")
        print(f"  OK ('You got it!') responses: {stats['ok_responses']}")
        print(f"  Segmentation-Fault responses: {stats['segfault_responses']}")
        print(f"  Other responses: {stats['other_responses']}")

def simulate_virtual_clients(num_clients: int, duration: int, ramp: float = 0.0):
    """
    Internally simulate 'num_clients' clients hitting the process_payload() function
    over 'duration' seconds. This performs no network I/O — it's purely in-process.
    Useful for observing how the server logic responds under load without sending traffic.

    - num_clients: total number of virtual "requests" to issue
    - duration: seconds over which to spread the simulated requests
    - ramp: fraction [0..1] describing front-loading (0=smooth uniform spacing)
    """
    print(f"[+] Starting fake-DDoS simulation: {num_clients} virtual requests over {duration}s...")
    start = time.time()
    threads = []
    # simple worker that calls process_payload with a mix of good/bad payloads
    def worker(payload: bytes):
        process_payload(payload)

    # create a simple mix of payloads
    import random
    def random_payload(i):
        # some valid 4-field payloads, some invalid, some exact BUFFER_SIZE
        r = random.random()
        if r < 0.05:
            # exact BUFFER_SIZE -> triggers segmentation fault response
            return b"A" * BUFFER_SIZE
        elif r < 0.6:
            # valid-ish 4-field CSV, but often incorrect numbers
            f1 = random.choice([332, 328, 999])
            f2 = random.randint(0, 12000)
            # sometimes correct f3
            f3 = random.choice([0xFFFFE000, random.randint(0, 0xFFFFFFFF)])
            f4 = random.randint(7000, 11000)
            return f"{f1},{f2},{hex(f3)},{f4}\n".encode('utf-8')
        else:
            # random short string
            return f"HELLO-{i}".encode('utf-8')

    for i in range(num_clients):
        payload = random_payload(i)
        t = threading.Thread(target=worker, args=(payload,), daemon=True)
        threads.append(t)
        t.start()
        # simple pacing to spread requests over duration
        if duration > 0:
            time.sleep(duration / max(1, num_clients))
    # wait for threads to finish
    for t in threads:
        t.join(timeout=1.0)
    end = time.time()
    print(f"[+] Simulation finished in {end - start:.2f}s")
    dump_stats()

def main():
    parser = argparse.ArgumentParser(description="Fake DDoS educational server/simulator")
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
        # Reset stats
        with lock:
            stats.update({k: 0 for k in stats})
        simulate_virtual_clients(args.virtual_clients, args.duration)
        return

    # else run the real TCP server
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
