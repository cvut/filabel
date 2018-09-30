from helper import run_ok, config, user, pr_labels

RADIOACTIVE_WASE = '\n'.join([
    f'  PR https://github.com/{user}/filabel-testrepo2/pull/{num} - OK'
    for num in reversed(range(1, 111+1))
]) + '\n'
RADIOACTIVE_WASE_ADD = RADIOACTIVE_WASE.replace('\n', '\n    + danger\n')
RADIOACTIVE_WASE_DEL = RADIOACTIVE_WASE.replace('\n', '\n    - danger\n')


auth = config("auth.real.cfg")


def test_radioactive_waste_empty():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo2')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo2 - OK
{RADIOACTIVE_WASE}'''
    assert pr_labels('filabel-testrepo2', 1) == []
    assert pr_labels('filabel-testrepo2', 42) == []
    assert pr_labels('filabel-testrepo2', 110) == []


def test_radioactive_waste_add():
    cp = run_ok(f'--config-labels "{config("labels.radiation.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo2')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo2 - OK
{RADIOACTIVE_WASE_ADD}'''
    assert pr_labels('filabel-testrepo2', 2) == ['danger']
    assert pr_labels('filabel-testrepo2', 55) == ['danger']
    assert pr_labels('filabel-testrepo2', 103) == ['danger']


# The last test, if your app works, would also remove all tags supplied by
# the previous tests
def test_radioactive_waste_remove():
    cp = run_ok(f'--config-labels "{config("labels.radiation_off.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo2')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo2 - OK
{RADIOACTIVE_WASE_DEL}'''
    assert pr_labels('filabel-testrepo2', 8) == []
    assert pr_labels('filabel-testrepo2', 69) == []
    assert pr_labels('filabel-testrepo2', 109) == []
