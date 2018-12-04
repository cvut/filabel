from helper import run, run_ok, config, user, pr_labels

auth = config("auth.real.cfg")


def test_empty_labels():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert set(cp.stdout.splitlines()) == set((
        f'REPO {user}/filabel-testrepo1 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK',
        f'REPO {user}/filabel-testrepo3 - OK',
    ))

    assert pr_labels('filabel-testrepo1', 1) == []
    assert pr_labels('filabel-testrepo1', 2) == []


def test_404_repos():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'hroncok/non-exsiting-repo MarekSuchanek/non-exsiting-repo')

    assert set(cp.stdout.splitlines()) == set((
        'REPO hroncok/non-exsiting-repo - FAIL',
        'REPO MarekSuchanek/non-exsiting-repo - FAIL',
    ))


def test_foreign_repos():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'hroncok/filabel-testrepo-everybody')

    assert 'REPO hroncok/filabel-testrepo-everybody - OK' in cp.stdout
    assert ('PR https://github.com/hroncok/filabel-testrepo-everybody/pull/1'
            ' - FAIL' in cp.stdout)
    assert cp.stdout.count('- OK\n') == 1


def test_abc_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    expected = (
        f'REPO {user}/filabel-testrepo1 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK',
        f'  + a',
        f'  + ab',
        f'  + abc',
        f'REPO {user}/filabel-testrepo3 - OK',
    )

    outlines = cp.stdout.splitlines()

    assert set(outlines) == set(expected)

    # this checks added labels are still sorted and right after the PR line
    s = outlines.index(expected[2])
    assert outlines.index(expected[3]) == s + 1
    assert outlines.index(expected[4]) == s + 2
    assert outlines.index(expected[5]) == s + 3

    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == []


def test_abc_labels_again():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    expected = (
        f'REPO {user}/filabel-testrepo1 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK',
        f'  = a',
        f'  = ab',
        f'  = abc',
        f'REPO {user}/filabel-testrepo3 - OK',
    )

    outlines = cp.stdout.splitlines()

    assert set(outlines) == set(expected)

    # this checks added labels are still sorted and right after the PR line
    s = outlines.index(expected[2])
    assert outlines.index(expected[3]) == s + 1
    assert outlines.index(expected[4]) == s + 2
    assert outlines.index(expected[5]) == s + 3

    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == []


def test_nine_labels():
    cp = run_ok(f'--config-labels "{config("labels.9.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    expected = (
        f'REPO {user}/filabel-testrepo1 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK',
        f'  + nine',
        f'  + ninenine',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK',
        f'REPO {user}/filabel-testrepo3 - OK',
    )

    outlines = cp.stdout.splitlines()

    assert set(outlines) == set(expected)

    # this checks added labels are still sorted and right after the PR line
    s = outlines.index(expected[1])
    assert outlines.index(expected[2]) == s + 1
    assert outlines.index(expected[3]) == s + 2

    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == ['nine', 'ninenine']


def test_empty_labels_wont_remove():
    cp = run_ok(f'--config-labels "{config("labels.empty.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert set(cp.stdout.splitlines()) == set((
        f'REPO {user}/filabel-testrepo1 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK',
        f'REPO {user}/filabel-testrepo3 - OK',
    ))

    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == ['nine', 'ninenine']


def test_empty_globs_remove_disabled():
    cp = run_ok(f'--config-labels "{config("labels.eraser.cfg")}" '
                f'--config-auth "{auth}" '
                f'--no-delete-old '
                f'--async '
                f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert set(cp.stdout.splitlines()) == set((
        f'REPO {user}/filabel-testrepo1 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/2 - OK',
        f'PR https://github.com/{user}/filabel-testrepo1/pull/1 - OK',
        f'REPO {user}/filabel-testrepo3 - OK',
    ))

    assert pr_labels('filabel-testrepo1', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo1', 2) == ['nine', 'ninenine']


def test_closed_prs_no_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" --async '
                f'{user}/filabel-testrepo4')

    assert set(cp.stdout.splitlines()) == set((
        f'REPO {user}/filabel-testrepo4 - OK',
        f'PR https://github.com/{user}/filabel-testrepo4/pull/3 - OK',
        f'  + ab',
        f'  + abc',
        f'PR https://github.com/{user}/filabel-testrepo4/pull/2 - OK',
        f'  + a',
        f'  + ab',
        f'  + abc',
    ))

    # added labels are still sorted and right after the PR line
    # is left out as an exercise for the reader

    assert pr_labels('filabel-testrepo4', 1) == []
    assert pr_labels('filabel-testrepo4', 2) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 3) == ['ab', 'abc']

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" --async '
        f'{user}/filabel-testrepo4')


def test_closed_prs_get_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'--state closed '
                f'--async '
                f'{user}/filabel-testrepo4')

    assert set(cp.stdout.splitlines()) == set((
        f'REPO {user}/filabel-testrepo4 - OK',
        f'PR https://github.com/{user}/filabel-testrepo4/pull/1 - OK',
        f'  + a',
        f'  + ab',
        f'  + abc',
    ))

    assert pr_labels('filabel-testrepo4', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 2) == []
    assert pr_labels('filabel-testrepo4', 3) == []

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" --async '
        f'--state closed '
        f'{user}/filabel-testrepo4')


def test_all_prs_get_labels():
    cp = run_ok(f'--config-labels "{config("labels.abc.cfg")}" '
                f'--config-auth "{auth}" '
                f'--state all '
                f'--async '
                f'{user}/filabel-testrepo4')
    outlines = cp.stdout.splitlines()

    assert outlines.count(f'REPO {user}/filabel-testrepo4 - OK') == 1
    assert outlines.count(f'PR https://github.com/{user}/'
                          f'filabel-testrepo4/pull/3 - OK') == 1
    assert outlines.count(f'PR https://github.com/{user}/'
                          f'filabel-testrepo4/pull/1 - OK') == 1
    assert outlines.count('  + a') == 2
    assert outlines.count('  + ab') == 3
    assert outlines.count('  + abc') == 3

    assert pr_labels('filabel-testrepo4', 1) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 2) == ['a', 'ab', 'abc']
    assert pr_labels('filabel-testrepo4', 3) == ['ab', 'abc']

    # should erase lables, courtesy
    run(f'--config-labels "{config("labels.eraser.cfg")}" '
        f'--config-auth "{auth}" '
        f'--state all --async '
        f'{user}/filabel-testrepo4')


# The last test, if your app works, would also remove all tags supplied by
# the previous tests
def test_empty_globs():
    run_ok(f'--config-labels "{config("labels.eraser.cfg")}" '
           f'--config-auth "{auth}" --async '
           f'{user}/filabel-testrepo1 {user}/filabel-testrepo3')

    assert pr_labels('filabel-testrepo1', 1) == []
    assert pr_labels('filabel-testrepo1', 2) == []
