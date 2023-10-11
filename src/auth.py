import base64
import json
import logging
import os
import signal
import time
from urllib.parse import urlencode, quote_plus

import requests
from flask import Flask, request

from src.shared import realpath_type


def login_user(args):
    token_file = args.token_file
    app = Flask(__name__)
    client_id = os.getenv('COGNITO_CLIENT_ID')
    auth_url = os.getenv('AUTH_URL')

    @app.route('/authenticated', methods=['GET'])
    def authenticated():
        auth_code = request.args.get('code')
        try:
            data = {'grant_type':   'authorization_code', 'client_id': client_id, 'code': auth_code,
                    'redirect_uri': callback_endpoint}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(f'{auth_url}/oauth2/token', headers=headers, data=urlencode(data))
            tokens = json.dumps(response.json(), indent=4)
            with open(token_file, 'w') as file:
                file.write(tokens)
            logging.debug(f'Token (ID, Access, Refresh) written to file: {token_file}')
            os.kill(os.getpid(), signal.SIGINT)  # SIGTERM) #SIGKILL)
            return 'You are authenticated', 200
        except Exception as error:
            logging.error(f'Error getting tokens: {error}')
            return 'Error getting tokens', 500

    port = 3000
    callback_url = f'http://localhost:{port}'
    callback_endpoint = f'{callback_url}/authenticated'
    encoded_url = quote_plus(callback_endpoint)
    scope = "email+openid+phone"
    response_type = "code"
    login_url = f'{auth_url}/login?client_id={client_id}&response_type={response_type}&scope={scope}&redirect_uri={encoded_url}'
    logging.info(f'Visit and login at: {login_url}')
    logging.info(f'App listening at {callback_url}')
    app.run(port=port)


def is_token_expired(token_file):
    tokens = read_tokens(token_file)
    if 'id_token' not in tokens:
        return True
    id_token = tokens['id_token']
    decoded_token = decode_auth_token(id_token)
    expiration_time = decoded_token.get('exp')
    current_time = time.time()
    if expiration_time:
        # AWS Cognito returns time in seconds, while Python's time() function returns time in milliseconds
        return current_time > expiration_time
    else:
        raise ValueError('No expiration time in token')


def decode_auth_token(auth_token):
    parts = auth_token.split('.')  # split the token into its three components (header, payload, signature)
    if len(parts) != 3:
        raise ValueError('ID token has invalid format')
    payload = parts[1]  # base64 decode and JSON parse the payload
    payload += '=' * ((4 - len(payload) % 4) % 4)  # add padding
    decoded_payload = base64.b64decode(payload)
    json_payload = json.loads(decoded_payload)
    return json_payload


def refresh_token(args):
    token_file = args.token_file
    auth_url = os.getenv('AUTH_URL')
    url = f"{auth_url}/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    tokens = read_tokens(token_file)
    client_id = os.getenv('COGNITO_CLIENT_ID')
    data = {'grant_type': 'refresh_token', 'client_id': client_id, 'refresh_token': tokens['refresh_token']}
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    if response.status_code != 200:
        logging.error('Error: Unable to refresh token')
        exit(1)

    tokens['id_token'] = response_data['id_token']
    tokens['access_token'] = response_data['access_token']

    with open(token_file, 'w') as f:
        try:
            json.dump(tokens, f, indent=4)
            logging.debug(f'Token (ID, Access, Refresh) updated in file: {token_file}')
        except Exception as e:
            # except BotoCoreError as e:
            logging.error(f'Error writing to file: {e}')
            exit(1)


def read_tokens(token_file):
    with open(token_file, 'r') as f:
        tokens = json.load(f)
    if 'refresh_token' not in tokens:
        logging.warning(f'No refresh token found in file: {token_file}')
        # exit(1)
    if 'access_token' not in tokens:
        logging.warning(f'No access token found in file: {token_file}')
        # exit(1)
    if 'id_token' not in tokens:
        logging.warning(f'No ID token found in file: {token_file}')
        # exit(1)
    return tokens


def login_or_refresh_token(args):
    if not os.path.exists(args.token_file):
        login_user(args)
    elif is_token_expired(args.token_file):
        refresh_token(args)
    else:
        logging.debug('Token is still valid')


def add_token_file_arg(parser):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    parser.add_argument("-t", "--token-file", dest='token_file', type=realpath_type, help="Token file location",
                        default=os.path.join(script_dir, 'tokens.json'))


def dump_token(args):
    login_or_refresh_token(args)
    claims = decode_auth_token(read_tokens(args.token_file)['id_token'])
    logging.info(json.dumps(claims, indent=4))


def add_token_command(subparsers):
    parser = subparsers.add_parser("token", help="Read and manage tokens")
    add_token_file_arg(parser)
    token_subparsers = parser.add_subparsers(dest="token_command", help="Token subcommands")
    dump = token_subparsers.add_parser("dump", help="Dump token info")
    dump.set_defaults(func=dump_token)
    login = token_subparsers.add_parser("login", help="Force login (token refresh normally handles this)")
    login.set_defaults(func=login_user)
    refresh = token_subparsers.add_parser("refresh", help="Refresh token")
    refresh.set_defaults(func=login_or_refresh_token)
    return {"token": parser}


def get_sub(token_file):
    tokens = read_tokens(token_file)
    id_token = tokens['id_token']
    decoded_token = decode_auth_token(id_token)
    sub = decoded_token.get('sub')
    return sub
