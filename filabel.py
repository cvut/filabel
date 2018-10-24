import configparser
import click
import enum
import fnmatch
import itertools
import requests


class GitHub:
    """
    This class can communicate with the GitHub API
    just give it a token and go.
    """
    API = 'https://api.github.com'

    def __init__(self, token, session=None):
        """
        token: GitHub token
        session: optional requests session
        """
        self.token = token
        self.session = session or requests.Session()
        self.session.headers = {'User-Agent': 'filabel'}
        self.session.auth = self._token_auth

    def _token_auth(self, req):
        """
        This alters all our outgoing requests
        """
        req.headers['Authorization'] = 'token ' + self.token
        return req

    def _paginated_json_get(self, url, params=None):
        r = self.session.get(url, params=params)
        r.raise_for_status()
        json = r.json()
        if 'next' in r.links and 'url' in r.links['next']:
            json += self._paginated_json_get(r.links['next']['url'], params)
        return json

    def user(self):
        """
        Get current user authenticated by token
        """
        return self._paginated_json_get(f'{self.API}/user')

    def pull_requests(self, owner, repo, state='open', base=None):
        """
        Get all Pull Requests of a repo

        owner: GtiHub user or org
        repo: repo name
        state: open, closed, all
        base: optional branch the PRs are open for
        """
        params = {'state': state}
        if base is not None:
            params['base'] = base
        url = f'{self.API}/repos/{owner}/{repo}/pulls'
        return self._paginated_json_get(url, params)

    def pr_files(self, owner, repo, number):
        """
        Get files of one Pull Request

        owner: GtiHub user or org
        repo: repo name
        number: PR number/id
        """
        url = f'{self.API}/repos/{owner}/{repo}/pulls/{number}/files'
        return self._paginated_json_get(url)

    def pr_filenames(self, owner, repo, number):
        """
        Get filenames of one Pull Request. A generator.

        owner: GtiHub user or org
        repo: repo name
        number: PR number/id
        """
        return (f['filename'] for f in self.pr_files(owner, repo, number))

    def reset_labels(self, owner, repo, number, labels):
        """
        Set's labels for Pull Request. Replaces all existing lables.

        owner: GtiHub user or org
        repo: repo name
        lables: all lables this PR will have
        """
        url = f'{self.API}/repos/{owner}/{repo}/issues/{number}'
        r = self.session.patch(url, json={'labels': labels})
        r.raise_for_status()
        return r.json()['labels']


class Change(enum.Enum):
    """
    Enumeration of possible label changes
    """
    ADD = 1
    DELETE = 2
    NONE = 3


class Report:
    """
    Simple container for reporting repo-pr label changes
    """
    def __init__(self, repo):
        self.repo = repo
        self.ok = True
        self.prs = {}


class Filabel:
    """
    Main login of PR labeler
    """
    def __init__(self, token, labels,
                 state='open', base=None, delete_old=True):
        """
        token: GitHub token
        labels: Configuration of labels with globs
        state: State of PR to be (re)labeled
        base: Base branch of PRs to be (re)labeled
        delete_old: If no longer matching labels should be deleted
        """
        self.github = GitHub(token)
        self.labels = labels
        self.state = state
        self.base = base
        self.delete_old = delete_old

    @property
    def defined_labels(self):
        """
        Set of labels defined in configuration
        """
        return set(self.labels.keys())

    def _matching_labels(self, pr_filenames):
        """
        Find matching labels based on given filenames

        pr_filenames: list of filenames as strings
        """
        labels = set()
        for filename in pr_filenames:
            for label, patterns in self.labels.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        labels.add(label)
                        break
        return labels

    def _compute_labels(self, defined, matching, existing):
        """
        Compute added, remained, deleted, and future label sets

        defined: Set of defined labels in config
        matching: Set of matching labels that should be in PR
        existing: Set of labels that are currently in PR
        """
        added = matching - existing
        remained = matching & existing
        deleted = set()
        future = existing
        if self.delete_old:
            deleted = (existing & defined) - matching
            future = existing - defined
        future = future | matching
        return added, remained, deleted, future

    def run_pr(self, owner, repo, pr_dict):
        """
        Manage labels for single given PR

        owner: Owner of GitHub repository
        repo: Name of GitHub repository
        pr_dict: PR as dict from GitHub API
        """
        pr_filenames = list(
            self.github.pr_filenames(owner, repo, pr_dict['number'])
        )
        added, remained, deleted, future = self._compute_labels(
            self.defined_labels,
            self._matching_labels(pr_filenames),
            set(l['name'] for l in pr_dict['labels'])
        )

        new_labels = self.github.reset_labels(
            owner, repo, pr_dict['number'], list(future)
        )

        new_label_names = set(l['name'] for l in new_labels)
        return sorted(itertools.chain(
            [(a, Change.ADD) for a in added],
            [(r, Change.NONE) for r in remained],
            [(d, Change.DELETE) for d in deleted]
        )) if future == new_label_names else None

    def run_repo(self, reposlug):
        """
        Manage labels for all matching PRs in given repo

        reposlug: Reposlug (full name) of GitHub repo (i.e. "owner/name")
        """
        report = Report(reposlug)
        owner, repo = reposlug.split('/')
        try:
            prs = self.github.pull_requests(owner, repo, self.state, self.base)
        except Exception:
            report.ok = False
            return report

        for pr_dict in prs:
            url = pr_dict.get('html_url', 'unknown')
            report.prs[url] = None
            try:
                report.prs[url] = self.run_pr(owner, repo, pr_dict)
            except Exception:
                pass
        return report


def parse_labels(cfg):
    """
    Parse labels to dict where label is key and list
    of patterns is corresponding value

    cfg: ConfigParser with loaded configuration of labels
    """
    return {
        label: list(filter(None, cfg['labels'][label].splitlines()))
        for label in cfg['labels']
    }


def stylize_label_change(change_type, label):
    """
    Stylize change with given type and changed label

    change_type: type of change
    label: name of changed label
    """
    if change_type == Change.ADD:
        return click.style(f'+ {label}', fg='green')
    if change_type == Change.DELETE:
        return click.style(f'- {label}', fg='red')
    return f'= {label}'


def print_report(report):
    """
    Print Filabel report to command line

    report: Report to be printed
    """
    click.secho(f'REPO', nl=False, bold=True)
    click.secho(f' {report.repo} - ', nl=False)
    if report.ok:
        click.secho('OK', fg='green', bold=True)
        for pr_link, result in report.prs.items():
            click.secho(f'  PR', nl=False, bold=True)
            click.secho(f' {pr_link} - ', nl=False)
            if result is None:
                click.secho('FAIL', fg='red', bold=True)
            else:
                click.secho('OK', fg='green', bold=True)
                for label, t in result:
                    click.echo(f'    {stylize_label_change(t, label)}')
    else:
        click.secho('FAIL', fg='red', bold=True)


def get_token(config_auth):
    """
    Extract token from auth config and do the checks

    config_auth: ConfigParser with loaded configuration of auth
    """
    if config_auth is None:
        click.secho('Auth configuration not supplied!', err=True)
        exit(1)
    try:
        cfg_auth = configparser.ConfigParser()
        cfg_auth.read_file(config_auth)
        return cfg_auth.get('github', 'token')
    except Exception:
        click.secho('Auth configuration not usable!', err=True)
        exit(1)


def get_labels(config_labels):
    """
    Extract labels from labels config and do the checks

    config_labels: ConfigParser with loaded configuration of labels
    """
    if config_labels is None:
        click.secho('Labels configuration not supplied!', err=True)
        exit(1)
    try:
        cfg_labels = configparser.ConfigParser()
        cfg_labels.read_file(config_labels)
        return parse_labels(cfg_labels)
    except Exception:
        click.secho('Labels configuration not usable!', err=True)
        exit(1)


def check_reposlugs(reposlugs):
    """
    Check formatting of reposlugs (contains 1 "/")

    reposlugs: List of reposlugs (i.e. "owner/repo")
    """
    for reposlug in reposlugs:
        if len(reposlug.split('/')) != 2:
            click.secho(f'Reposlug {reposlug} not valid!', err=True)
            exit(1)


@click.command('filabel')
@click.argument('reposlugs', nargs=-1)
@click.option('-s', '--state', type=click.Choice(['open', 'closed', 'all']),
              default='open', show_default=True, help='Filter pulls by state.')
@click.option('-d/-D', '--delete-old/--no-delete-old', default=True,
              show_default=True,
              help='Delete labels that do not match anymore.')
@click.option('-b', '--base', type=str, metavar='BRANCH',
              help='Filter pulls by base (PR target) branch name.')
@click.option('-a', '--config-auth', type=click.File('r'),
              help='File with authorization configuration.')
@click.option('-l', '--config-labels', type=click.File('r'),
              help='File with labels configuration.')
def cli(reposlugs, state, delete_old, base, config_auth, config_labels):
    """
    CLI tool for filename-pattern-based labeling of GitHub PRs
    """
    token = get_token(config_auth)
    labels = get_labels(config_labels)
    check_reposlugs(reposlugs)

    fl = Filabel(token, labels, state, base, delete_old)
    for repo in reposlugs:
        report = fl.run_repo(repo)
        print_report(report)


if __name__ == '__main__':
    cli()
