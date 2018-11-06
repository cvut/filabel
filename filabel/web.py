import configparser
import flask
import hashlib
import hmac
import jinja2
import os

from filabel.logic import Filabel
from filabel.utils import parse_labels


def webhook_verify_signature(payload, signature, secret, encoding='utf-8'):
    """
    Verify the payload with given signature against given secret

    see https://developer.github.com/webhooks/securing/

    payload: received data as dict
    signature: included SHA1 signature of payload (with secret)
    secret: secret to verify signature
    encoding: encoding for secret (optional)
    """
    h = hmac.new(secret.encode(encoding), payload, hashlib.sha1)
    return hmac.compare_digest('sha1=' + h.hexdigest(), signature)


def process_webhook_pr(payload):
    """
    Process webhook event "pull_request"

    payload: event payload
    """
    filabel = flask.current_app.config['filabel']
    try:
        action = payload['action']
        pull_request = payload['pull_request']
        pr_number = payload['number']
        pr_url = pull_request['url'].split('/')  # no repo field in payload!
        owner = pr_url[-4]
        repo = pr_url[-3]
        reposlug = f'{owner}/{repo}'

        if action not in ('opened', 'synchronize'):
            flask.current_app.logger.info(
                f'Action {action} from {reposlug}#{pr_number} skipped'
            )
            return 'Accepted but action not processed', 202

        filabel.run_pr(owner, repo, pull_request)

        flask.current_app.logger.info(
            f'Action {action} from {reposlug}#{pr_number} processed'
        )
        return 'PR successfully filabeled', 200
    except (KeyError, IndexError):
        flask.current_app.logger.info(
            f'Incorrect data entity from IP {flask.request.remote_addr}'
        )
        flask.abort(422, 'Missing required payload fields')
    except Exception:
        flask.current_app.logger.error(
            f'Error occurred while processing {repo}#{pr_number}'
        )
        flask.abort(500, 'Processing PR error')


def process_webhook_ping(payload):
    """
    Process webhook event "ping"

    payload: event payload
    """
    try:
        repo = payload['repository']['full_name']
        hook_id = payload['hook_id']
        flask.current_app.logger.info(
            f'Accepting PING from {repo}#WH-{hook_id}'
        )
        return 'PONG', 200
    except KeyError:
        flask.current_app.logger.info(
            f'Incorrect data entity from IP {flask.request.remote_addr}'
        )
        flask.abort(422, 'Missing payload contents')


webhook_processors = {
    'pull_request': process_webhook_pr,
    'ping': process_webhook_ping
}


def create_app(*args, **kwargs):
    """
    Prepare Filabel Flask application listening to GitHub webhooks
    """
    app = flask.Flask(__name__)
    cfg = configparser.ConfigParser()
    if 'FILABEL_CONFIG' not in os.environ:
        app.logger.critical('Config not supplied by envvar FILABEL_CONFIG')
        exit(1)
    configs = os.environ['FILABEL_CONFIG'].split(':')
    cfg.read(configs)

    try:
        app.config['labels'] = parse_labels(cfg)
    except Exception:
        app.logger.critical('Labels configuration not usable!', err=True)
        exit(1)

    try:
        app.config['github_token'] = cfg.get('github', 'token')
        app.config['secret'] = cfg.get('github', 'secret', fallback=None)
    except Exception:
        app.logger.critical('Auth configuration not usable!', err=True)
        exit(1)

    filabel = Filabel(app.config['github_token'], app.config['labels'])

    try:
        app.config['github_user'] = filabel.github.user()
        app.config['filabel'] = filabel
    except Exception:
        app.logger.critical('Bad token: could not get GitHub user!', err=True)
        exit(1)

    @app.template_filter('github_user_link')
    def github_user_link_filter(github_user):
        """
        Template filter for HTML link to GitHub profile

        github_user: User data from GitHub API
        """
        url = flask.escape(github_user['html_url'])
        login = flask.escape(github_user['login'])
        return jinja2.Markup(f'<a href="{url}" target="_blank">{login}</a>')

    @app.route('/', methods=['GET'])
    def index():
        """
        Landing info page
        """
        return flask.render_template(
            'infopage.html',
            labels=flask.current_app.config['labels'],
            user=flask.current_app.config['github_user']
        )

    @app.route('/', methods=['POST'])
    def webhook_listener():
        """
        Webhook listener endpoint
        """
        signature = flask.request.headers.get('X-Hub-Signature', '')
        event = flask.request.headers.get('X-GitHub-Event', '')
        payload = flask.request.get_json()

        secret = flask.current_app.config['secret']

        if secret is not None and not webhook_verify_signature(
                flask.request.data, signature, secret
        ):
            flask.current_app.logger.warning(
                f'Attempt with bad secret from IP {flask.request.remote_addr}'
            )
            flask.abort(401, 'Bad webhook secret')

        if event not in webhook_processors:
            supported = ', '.join(webhook_processors.keys())
            flask.abort(400, f'Event not supported (supported: {supported})')

        return webhook_processors[event](payload)

    return app
