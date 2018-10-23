import atexit
import contextlib
import os
import pathlib
import requests
import shlex
import subprocess
import sys


def run(line, module=False, **kwargs):
    if module:
        print('$ python -m filabel', line)
        command = [sys.executable, '-m', 'filabel'] + shlex.split(line)
    else:
        print('$ filabel', line)
        command = ['filabel'] + shlex.split(line)
    return subprocess.run(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True,
                          **kwargs)


def run_ok(*args, **kwargs):
    cp = run(*args, **kwargs)
    assert cp.returncode == 0
    assert not cp.stderr
    print(cp.stdout)
    return cp


def config(name):
    return pathlib.Path(__file__).parent / 'fixtures' / name


@contextlib.contextmanager
def env(**kwargs):
    original = {key: os.getenv(key) for key in kwargs}
    os.environ.update({key: str(value) for key, value in kwargs.items()})
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value


try:
    user = os.environ['GH_USER']
    token = os.environ['GH_TOKEN']
except KeyError:
    raise RuntimeError('You must set GH_USER and GH_TOKEN environ vars')
else:
    config('auth.real.cfg').write_text(
        config('auth.fff.cfg').read_text().replace(40 * 'f', token)
    )
    atexit.register(config('auth.real.cfg').unlink)


def pr_labels(repo, prnum):
    # TODO set auth header if you hit rate limit
    return sorted(l['name'] for l in requests.get(
        f'https://api.github.com/repos/{user}/{repo}/pulls/{prnum}',
        headers={'Authorization': 'token ' + token},
    ).json()['labels'])
