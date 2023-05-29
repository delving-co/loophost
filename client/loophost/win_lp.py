import os
from subprocess import run
import sys
import threading
import win32serviceutil
import win32service
# import win32event
import servicemanager
import socket
import time
import logging
import concurrent.futures
from loophost import GET_LOOPHOST_DIR, HUBDIR

os.chdir(GET_LOOPHOST_DIR())


logging.basicConfig(
    filename="c:\\Users\\Public\\.loophost\\loophost-goproxy-service.log",
    level=logging.DEBUG,
    format="[loophost-service] %(levelname)-7.7s %(message)s",
)


class workingthread(threading.Thread):
    def __init__(self, quitEvent):
        self.quitEvent = quitEvent
        self.waitTime = 1
        threading.Thread.__init__(self)

    def run(self):
        try:
            # Running start_flask() function on different thread, so that it doesn't blocks the code
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
            executor.submit(self.start_flask)
        except Exception as e:
            print(e)

        # Following Lines are written so that, the program doesn't get quit
        # Will Run a Endless While Loop till Stop signal is not received from Windows Service API
        while not self.quitEvent.isSet():  # If stop signal is triggered, exit
            time.sleep(1)

    def start_flask(self):
        cmd = "bin\\loopproxy.exe /Users/Public/.loophost"
        run(
            cmd,
            shell=True,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            # stdin=subprocess.PIPE,
            cwd=HUBDIR,
            check=True,
        )


class LoopProxyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LoopProxy-Service"
    _svc_display_name_ = "LoopProxy Service"
    _svc_description_ = "This is my service"
    # _exe_name_ = "loopproxy-service.exe"

    def __init__(self, args):
        socket.setdefaulttimeout(60)
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = threading.Event()
        self.thread = workingthread(self.hWaitStop)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.hWaitStop.set()

    def SvcDoRun(self):
        self.thread.start()
        self.hWaitStop.wait()
        self.thread.join()


if __name__ == "__main__":
    print(f"Got {len(sys.argv)} arguments")
    if len(sys.argv) < 2:
        print("")
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LoopProxyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LoopProxyService)
