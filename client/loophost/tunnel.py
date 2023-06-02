""" Multiplex SSH reverse tunnels using multiprocessing
Watches the loophost.json file to determine if their are
new tunnels needed or tunnels that should be torn down."""

import json
from multiprocessing import Pipe, Process
from pathlib import Path
import signal
from subprocess import run
import subprocess
import sys
import time

# import signal
# import sys
# import logging
from typing import List

from loophost import DATA_FILE_PATH, GET_LOOPHOST_DIR, TUNNEL_DOMAIN, GET_FLINGUSER_NAME
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from command_runner import command_runner


def get_ssh_command(host):
    CWD = GET_LOOPHOST_DIR()
    cmd = " ".join([
            "/usr/bin/ssh",  # TODO(FULL SSH PATH EVERYWHERE)
            "-o ServerAliveInterval=60",
            "-o ExitOnForwardFailure=yes",
            "-o UserKnownHostsFile=/dev/null",
            "-o StrictHostKeyChecking=no",
            f"-i {CWD}/tunnelkey",
            "-p 2222",
            f"-R {host}:443:localhost:4433",
            f"{GET_FLINGUSER_NAME()}@{TUNNEL_DOMAIN}",
        ])
    return cmd


def ssh_tunnel_subprocess(conn, host):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    cmd = get_ssh_command(host)

    def some_function():
        # print(".", end=None)
        if conn.poll():
            return True
        return False
    exit_code, output = command_runner(cmd, shell=True, timeout=None, stop_on=some_function)
    # run(
    #     shell=False,
    #     cwd=GET_LOOPHOST_DIR(),
    #     stdin=conn,
    #     check=True
    # )


class ConfigHandler(FileSystemEventHandler):
    tunnel_processes: dict = {}  # List[(Process, Pipe)] = []
    hostnames: List[str] = []

    def __init__(self):
        super().__init__()
        self.load_hostnames()
        self.ensure_tunnels_running()

    def load_hostnames(self):
        self.hostnames = json.loads(Path.read_text(DATA_FILE_PATH())).get("share")

    def on_modified(self, event):
        print(event)
        self.load_hostnames()
        self.ensure_tunnels_running()

    def ensure_tunnels_running(self):
        current_tunnels = []
        for tunnel in self.tunnel_processes.keys():
            current_tunnels.append(tunnel)
        for host in self.hostnames:
            if host not in current_tunnels:
                self.start_tunnel(host)
        for host in current_tunnels:
            if host not in self.hostnames:
                self.stop_tunnel(host)

    def start_tunnel(self, host):
        print(f"Starting tunnel for {host}")
        parent_conn, child_conn = Pipe()
        p = Process(
            target=ssh_tunnel_subprocess,
            args=[child_conn, host],
            name=host,
        )
        self.tunnel_processes[host] = (p, parent_conn)
        p.start()

    def stop_tunnel(self, host):
        print(f"Stopping tunnel for {host}")
        if host not in self.tunnel_processes:
            return
        print(f"terminating {host}...")
        (tunnel, pipe) = self.tunnel_processes.get(host)
        pipe.send("please stop")
        del self.tunnel_processes[host]

    def stop_all_tunnels(self):
        for host, (tunnel, pipe) in self.tunnel_processes.items():
            pipe.send("please stop")
        self.tunnel_processes = {}


def watch_and_listen():
    event_handler = ConfigHandler()
    observer = Observer()
    observer.schedule(event_handler, GET_LOOPHOST_DIR(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt...")
        observer.stop()
        event_handler.stop_all_tunnels()
    print("Waiting for observer thread to rejoin...")
    observer.join(timeout=1)


if __name__ == "__main__":
    watch_and_listen()
