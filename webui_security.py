import os
from pathlib import Path


def launch_options(workspace, environ=None):
    env = os.environ if environ is None else environ
    host = env.get('GRADIO_SERVER_NAME', '127.0.0.1').strip()
    if not host:
        raise ValueError('GRADIO_SERVER_NAME boş olamaz.')
    user = env.get('GRADIO_USER', '')
    password = env.get('GRADIO_PASSWORD', '')
    supplied = 'GRADIO_USER' in env or 'GRADIO_PASSWORD' in env
    if supplied and (not user.strip() or not password.strip()):
        raise ValueError('GRADIO_USER ve GRADIO_PASSWORD birlikte ve boş olmayacak şekilde tanımlanmalıdır.')
    auth = (user, password) if supplied else None
    if host not in {'127.0.0.1', 'localhost', '::1'} and auth is None:
        raise ValueError('Dış ağda WebUI açmak için GRADIO_USER ve GRADIO_PASSWORD zorunludur.')
    return {
        'server_name': host,
        'server_port': 7860,
        'share': False,
        'auth': auth,
        'allowed_paths': [str((Path(workspace) / 'web_out').resolve())],
    }
