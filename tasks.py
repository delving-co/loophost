import os
from pathlib import Path
import shutil
from invoke import task

packages = ['client']

@task
def clean(c, docs=False):
    print("Cleaning build artifacts...")
    patterns = [Path('dist'), Path('loopproxy','loophost'), Path('client','loophost','loophost')]
    if docs:
        patterns.append(Path('docs','_build'))
    for pattern in patterns:
        shutil.rmtree(pattern, ignore_errors=True)
    os.makedirs("dist", exist_ok=True)


@task()
def build_go(c):
    with c.cd("loopproxy"):
        c.run('go build -ldflags="-extldflags=-static" -tags osusergo,netgo -v')
    try:
        shutil.move(Path("loopproxy", "loopproxy.exe"), Path("client", "loophost", "loopproxy.exe"))
    except: 
        pass
    try:
        shutil.move(Path("loopproxy", "loopproxy"), Path("client", "loophost", "loopproxy"))
    except:
        pass

@task()
def build_poetry(c):
    for package in packages:
        with c.cd(package):
            c.run("poetry build")

@task(pre=[clean, build_go, build_poetry])
def build(c, docs=False):
    pass

