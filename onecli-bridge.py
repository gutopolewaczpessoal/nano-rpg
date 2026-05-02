#!/usr/bin/env python3
"""
Forwards TCP connections from 172.17.0.1:10255 to 127.0.0.1:10255.
This lets Docker containers reach the OneCLI proxy via host.docker.internal.
"""
import socket
import threading
import sys

LISTEN_HOST = "172.17.0.1"
LISTEN_PORT = 10255
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 10255

def relay(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            src.close()
        except OSError:
            pass
        try:
            dst.close()
        except OSError:
            pass

def handle(client):
    try:
        server = socket.create_connection((TARGET_HOST, TARGET_PORT))
    except OSError as e:
        print(f"Forward connect failed: {e}", flush=True)
        client.close()
        return
    t = threading.Thread(target=relay, args=(server, client), daemon=True)
    t.start()
    relay(client, server)

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((LISTEN_HOST, LISTEN_PORT))
    srv.listen(128)
    print(f"Forwarding {LISTEN_HOST}:{LISTEN_PORT} -> {TARGET_HOST}:{TARGET_PORT}", flush=True)
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()

if __name__ == "__main__":
    main()
