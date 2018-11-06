import re

from helper import run

hlp = run('--help')
stdout = hlp.stdout


def test_usage():
    assert stdout.startswith('Usage: filabel [OPTIONS] [REPOSLUGS]...')


def test_description():
    assert (
        'CLI tool for filename-pattern-based labeling of GitHub PRs' in stdout
    )


def test_help_when_m():
    hlp = run('--help', module=True)
    assert 'CLI tool for filename-pattern-based' in hlp.stdout


def test_state():
    assert re.search(r'-s,\s+--state\s+\[open\|closed\|all\]\s+'
                     r'Filter pulls by state\.\s+\[default:\s+open\]', stdout)


def test_delete_old():
    assert re.search(r'-d, --delete-old / -D, --no-delete-old\s+'
                     r'Delete labels that do not\s+match\s+anymore\.'
                     r'\s+\[default:\s+True\]', stdout)


def test_branch():
    assert re.search(r'-b,\s+--base\s+BRANCH\s+'
                     r'Filter pulls by base \(PR\s+target\)\s+branch\s+name\.',
                     stdout)


def test_config_auth():
    assert re.search(r'-a,\s+--config-auth\s+FILENAME\s+'
                     r'File with authorization\s+configuration\.',
                     stdout)


def test_config_labels():
    assert re.search(r'-l,\s+--config-labels\s+FILENAME\s+'
                     r'File with labels\s+configuration\.',
                     stdout)
