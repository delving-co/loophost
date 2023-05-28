import os
import pathlib
import sys
import threading
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import concurrent.futures
from loophost.flingroute import admin
from loophost import GET_LOOPHOST_DIR

os.chdir(GET_LOOPHOST_DIR())

logging.basicConfig(
    filename = 'c:\\Users\\Public\\.loophost\\loophost-hub.log',
    level = logging.DEBUG, 
    format = '[loophost-service] %(levelname)-7.7s %(message)s'
)

logging.debug("Loaded WinHub script")

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
        except:
            pass

        # Following Lines are written so that, the program doesn't get quit
        # Will Run a Endless While Loop till Stop signal is not received from Windows Service API
        while not self.quitEvent.isSet():  # If stop signal is triggered, exit
            time.sleep(1)

    def start_flask(self):
        logging.debug("Starting the web interface on port 5816")
        admin.run(host="0.0.0.0", port=5816)



class LoophostHubService (win32serviceutil.ServiceFramework):
    _svc_name_ = "LoophostHub-Service"
    _svc_display_name_ = "LoophostHub Service"
    _svc_description_ = "Web interface for configuring loophost"
    
    def __init__(self,args):
        logging.debug("Inside the Loophost HubService service")
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LoophostHubService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LoophostHubService)