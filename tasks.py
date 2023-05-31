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


@task()
def build_go(c):
    with c.cd("loopproxy"):
        if platform.system().lower().startswith('win'):
            c.run('go build -ldflags="-extldflags=-static" -tags osusergo,netgo -v -o loopproxy.exe')
            try:
                shutil.move(Path("loopproxy", "loopproxy.exe"), Path("client", "loophost", "loopproxy.exe"))
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


@task(pre=[clean, build_go, build_poetry])
def build(c, docs=False):
    pass
