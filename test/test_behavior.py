from helper import run, run_ok, config, user, pr_labels

auth = config("auth.real.cfg")


def test_empty_labels():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == []
    assert pr_labels('filabel-testrepo1', 2) == []


def test_404_repos():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" '
                f'hroncok/non-exsiting-repo MarekSuchanek/non-exsiting-repo')

    assert '\n' + cp.stdout == f'''
REPO hroncok/non-exsiting-repo - FAIL
REPO MarekSuchanek/non-exsiting-repo - FAIL
'''


def test_foreign_repos():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'hroncok/filabel-testrepo-everybody')

    assert 'REPO hroncok/filabel-testrepo-everybody - OK' in cp.stdout
    assert ('  PR https://github.com/hroncok/filabel-testrepo-everybody/pull/1'
            ' - FAIL' in cp.stdout)
    assert cp.stdout.count('- OK\n') == 1


def test_abc_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
    + a
    + ab
    + abc
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == []


def test_abc_labels_again():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
    = a
    = ab
    = abc
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == []


def test_nine_labels():
    cp = run_ok(f'--config-labels "{config("labels.9.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
    + nine
    + ninenine
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == ['nine', 'ninenine']


def test_empty_labels_wont_remove():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == ['nine', 'ninenine']


def test_empty_globs_remove_disabled():
    cp = run_ok(f'--config-labels "{config("labels.eraser.cfg")}" '
                f'--config-auth "{auth}" '
                f'--no-delete-old '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == ['nine', 'ninenine']


def test_closed_prs_no_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo4')
    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo4 - OK
  PR https://github.com/{user}/filabel-testrepo4/pull/3 - OK
    + ab
    + abc
  PR https://github.com/{user}/filabel-testrepo4/pull/2 - OK
    + a
    + ab
    + abc
'''
    assert pr_labels('filabel-testrepo4', 1) == []
    assert pr_labels('filabel-testrepo4', 2) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 3) == ['ab', 'abc']

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" '
        f'{user}/filabel-testrepo4')


def test_closed_prs_get_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'--state closed '
                f'{user}/filabel-testrepo4')
    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo4 - OK
  PR https://github.com/{user}/filabel-testrepo4/pull/1 - OK
    + a
    + ab
    + abc
'''
    assert pr_labels('filabel-testrepo4', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 2) == []
    assert pr_labels('filabel-testrepo4', 3) == []

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" '
        f'--state closed '
        f'{user}/filabel-testrepo4')


def test_all_prs_get_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'--state all '
                f'{user}/filabel-testrepo4')
    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo4 - OK
  PR https://github.com/{user}/filabel-testrepo4/pull/3 - OK
    + ab
    + abc
  PR https://github.com/{user}/filabel-testrepo4/pull/2 - OK
    + a
    + ab
    + abc
  PR https://github.com/{user}/filabel-testrepo4/pull/1 - OK
    + a
    + ab
    + abc
'''
    assert pr_labels('filabel-testrepo4', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 2) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 3) == ['ab', 'abc']

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" '
        f'--state all '
        f'{user}/filabel-testrepo4')


def test_master_base():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'--base master '
                f'{user}/filabel-testrepo4')
    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo4 - OK
  PR https://github.com/{user}/filabel-testrepo4/pull/2 - OK
    + a
    + ab
    + abc
'''
    assert pr_labels('filabel-testrepo4', 2) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 3) == []

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" '
        f'{user}/filabel-testrepo4')


def test_custom_base():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'--base pr_open '
                f'{user}/filabel-testrepo4')
    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo4 - OK
  PR https://github.com/{user}/filabel-testrepo4/pull/3 - OK
    + ab
    + abc
'''
    assert pr_labels('filabel-testrepo4', 2) == []
    assert pr_labels('filabel-testrepo4', 3) == ['ab', 'abc']

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" '
        f'{user}/filabel-testrepo4')



def test_diffs():
    cp = run_ok(f'--config-labels "{config("labels.changer.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3 '
                f'hroncok/non-exisitng-repo ')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
    + eight
    - nine
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
    = a
    - ab
    = abc
    + cd
REPO {user}/filabel-testrepo3 - OK
REPO hroncok/non-exisitng-repo - FAIL
'''
    assert pr_labels('filabel-testrepo1', 1) == ['a', 'abc', 'cd']
    assert pr_labels('filabel-testrepo1', 2) == ['eight', 'ninenine']



# The last test, if your app works, would also remove all tags supplied by
# the previous tests
def test_empty_globs():
    cp = run_ok(f'--config-labels "{config("labels.eraser.cfg")}" '
                f'--config-auth "{auth}" '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert '\n' + cp.stdout == f'''
REPO {user}/filabel-testrepo1 - OK
  PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK
    - eight
    - ninenine
  PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK
    - a
    - abc
    - cd
REPO {user}/filabel-testrepo3 - OK
'''
    assert pr_labels('filabel-testrepo1', 1) == []
    assert pr_labels('filabel-testrepo1', 2) == []
