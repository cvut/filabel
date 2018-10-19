import flask

from helper import env, config, user

config_env = f'{config("auth.real.cfg")}:{config("labels.empty.cfg")}'


def _import_app():
    import filabel
    if hasattr(filabel, 'app'):
        return filabel.app
    elif hasattr(filabel, 'create_app'):
        return filabel.create_app(None)
    else:
        raise RuntimeError(
            "Can't find a Flask app. "
            "Either instantiate `filabel.app` variable "
            "or implement `filabel.create_app(dummy)` function. "
            "See http://flask.pocoo.org/docs/1.0/patterns/appfactories/ "
            "for additional information."
        )


def _test_app():
    app = _import_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_app_imports():
    with env(FILABEL_CONFIG=config_env):
        app = _import_app()
        assert isinstance(app, flask.Flask)


def test_app_get_has_username():
    with env(FILABEL_CONFIG=config_env):
        app = _test_app()
        assert user in app.get('/').get_data(as_text=True)


# If you change this, the Signature bellow must be updated!
PING = {
    'zen': 'Approachable is better than simple.',
    'hook_id': 123456,
    'hook': {
        'type': 'Repository',
        'id': 55866886,
        'name': 'web',
        'active': True,
        'events': [
            'pull_request',
        ],
        'config': {
            'content_type': 'json',
            'insecure_ssl': '0',
            'secret': '********',
        },
    },
    'repository': {
        'id': 123456,
        'name': 'filabel-testrepo-everybody',
        'full_name': 'hroncok/filabel-testrepo-everybody',
        'private': False,
    },
    'sender': {
        'login': 'user',
    },
}


def test_ping_pongs():
    with env(FILABEL_CONFIG=config_env):
        app = _test_app()
        rv = app.post('/', json=PING, headers={
            'X-Hub-Signature': 'sha1=7528bd9a5b9d6546b0c221cacacc4207bdd4a51a',
            'X-GitHub-Event': 'ping'})
        assert rv.status_code == 200


def test_bad_secret():
    with env(FILABEL_CONFIG=config_env):
        app = _test_app()
        rv = app.post('/', json=PING, headers={
            'X-Hub-Signature': 'sha1=1cacacc4207bdd4a51a7528bd9a5b9d6546b0c22',
            'X-GitHub-Event': 'ping'})
        assert rv.status_code >= 400
