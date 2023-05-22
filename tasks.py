from invoke import task

packages = ['client']

@task
def clean(c, docs=False, bytecode=False, extra=''):
    print("Cleaning build artifacts...")
    patterns = ['dist', 'loopproxy/loophost', 'client/loophost/loophost']
    if docs:
        patterns.append('docs/_build')
    if bytecode:
        patterns.append('**/*.pyc')
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task(pre=[clean])
def build(c, docs=False):
    c.run("mkdir -p dist")
    with c.cd("loopproxy"):
        c.run('go build -ldflags="-extldflags=-static" -tags osusergo,netgo -v')
        c.run("mv loopproxy ../client/loophost/loopproxy")
    for package in packages:
        with c.cd(package):
            c.run("poetry build")
