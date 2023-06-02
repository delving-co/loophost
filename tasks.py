import os
from pathlib import Path
import platform
import shutil
from invoke import task


packages = ['client']


@task
def clean(c, docs=False):
    print("Cleaning build artifacts...")
    patterns = [Path('dist'), Path('loopproxy', 'loophost'), Path('client', 'loophost', 'loophost')]
    if docs:
        patterns.append(Path('docs', '_build'))
    for pattern in patterns:
        shutil.rmtree(pattern, ignore_errors=True)
    os.makedirs("dist", exist_ok=True)


@task
def build_win(c):
    if platform.system().lower().startswith('win'):
        print("Building windows service binaries")
    # Notes for the windows build and installer
    # MAKE SURE pywin32 is properly installed first after the pip install
    # cd C:\Users\joshuamckenty\.pyenv\pyenv-win\versions\3.10.5
    # python Scripts/pywin32_postinstall.py -install

    # BUILD a single binary for each key service
    # cd C:\Users\joshuamckenty\projects\loophost\client
    # pyinstaller --onefile --hidden-import win32timezone loophost\win_hub.py

    # DURING INSTALL, the services have to go into the pywin32 folder location
    # FOR /F %i IN
    #   ('python -c "import os; import win32service; print(os.path.dirname(win32service.__file__) + '\lib')"')
    #   DO set pywinpath=%i
    # copy dist\win_hub.exe %pywinpath%\

    # CHECK for a running process by looking at the port
    # // Get-Process -Id (Get-NetTCPConnection -LocalPort 443).OwningProcess


@task()
def build_go(c):
    with c.cd("loopproxy"):
        if platform.system().lower().startswith('win'):
            c.run('go build -ldflags="-extldflags=-static" -tags osusergo,netgo -v -o loopproxy.exe')
            try:
                shutil.move(Path("loopproxy", "loopproxy.exe"), Path("client", "loophost", "bins", "loopproxy.exe"))
            except Exception as e:
                print(e)
        else:
            platforms = ['linux', 'darwin']
            arches = ['arm64', 'amd64']
            for p in platforms:
                for a in arches:
                    c.run(f'GOOS={p} GOARCH={a} go build \
                        -ldflags="-extldflags=-static" \
                        -tags osusergo,netgo \
                        -o loopproxy-{p}-{a}')
                    try:
                        c.run(f"mv loopproxy-{p}-{a} ../client/loophost/bins/loopproxy-{p}-{a}")
                    except Exception as e:
                        print(e)


@task()
def build_poetry(c):
    for package in packages:
        with c.cd(package):
            c.run("poetry build --no-cache --format=wheel")


@task(pre=[clean, build_win, build_go, build_poetry])
def build(c, docs=False):
    pass
