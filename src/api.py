import json
import logging
import os

import requests

from src.shared import add_name_arg, add_thread_arg, add_prefix_arg, \
    add_collection_arg, add_file_arg
from src.auth import read_tokens, login_or_refresh_token, add_token_file_arg


def get_user(args):
    logging.info("Getting current user")
    url = os.getenv('BACKEND_URL') + '/user'
    response = api("get", args, url)
    user = response.json()['user']
    logging.info("Username: "+ user['username'])
    logging.info("Email: "+ user['email'])


def get_uploads(args):
    logging.info("Listing uploaded files")
    url = os.getenv('BACKEND_URL') + '/uploads'
    api("get", args, url)


def get_uploads_file(args):
    logging.info(f"Get uploaded file {args.prefix}")
    url = f'{os.getenv("BACKEND_URL")}/uploads/{args.prefix}'
    api("get", args, url)


def post_uploads_file(args):
    name = args.name or os.path.basename(args.file)
    logging.info(f"Uploading {args.file} to prefix {name} (via API)")
    url = f'{os.getenv("BACKEND_URL")}/uploads/{name}'
    files = {'file': open(args.file, 'rb')}
    api("post", args, url, files=files)


def put_uploads_file(args):
    name = args.name or os.path.basename(args.file)
    logging.info(f"Uploading {args.file} to prefix {name} (via S3)")
    # url = f'{os.getenv("BACKEND_URL")}/uploads/{name}'
    # files = {'file': open(args.file, 'rb')}
    # api("post", args, url, files=fil    print("Pre-signing file...")

    backend_url = os.environ['BACKEND_URL']
    url = f'{backend_url}/uploads/{name}'
    content_type = 'text/x-markdown'
    json_data = {
        'contentType': content_type
    }

    response = api("put", args, url, json=json_data)

    print(f"Status: {response.status_code}")
    print(f"Headers...\n{response.headers}")
    print(f"Data: {response.json()}")

    print("Uploading file to S3...")
    with open(args.file, 'rb') as f:
        file_data = f.read()

    upload_response = requests.put(response.json()['uploadUrl'], data=file_data, headers={'Content-Type': content_type})

    print(f"Status: {upload_response.status_code}")
    print(f"Headers...\n{upload_response.headers}")


def delete_uploads_file(args):
    logging.info(f"Deleting {args.prefix}")
    url = f'{os.getenv("BACKEND_URL")}/uploads/{args.prefix}'
    api("delete", args, url)


def post_index_file(args):
    logging.info(f"Indexing collection '{args.collection}' with prefix {args.prefix}")
    url = f'{os.getenv("BACKEND_URL")}/index/{args.collection}/{args.prefix}'
    api("post", args, url)


def post_index(args):
    logging.debug(f"Prompting collection '{args.collection}' with query '{args.query}'")
    # url = f'{os.getenv("BACKEND_URL")}/index'
    # api("get", args, url, json={"collection": args.collection, "query": args.query})
    url = f'{os.getenv("BACKEND_URL")}/index/{args.collection}'
    params = {}
    if args.parent_id:
        params |= {"parent_message_id": args.parent_id}
    api("post", args, url, json={"query": args.query}, params=params)


def get_index(args):
    logging.debug(f"Listing collections")
    url = f'{os.getenv("BACKEND_URL")}/index'
    params = {}
    api("get", args, url, params=params)


def delete_index(args):
    logging.debug(f"Deleting collection '{args.collection}'")
    url = f'{os.getenv("BACKEND_URL")}/index/{args.collection}'
    params = {}
    api("delete", args, url, params=params)


def get_threads(args):
    logging.debug("Listing threads")
    url = os.getenv('BACKEND_URL') + '/threads'
    api("get", args, url)


def get_thread_messages(args):
    logging.debug("Listing thread messages")
    url = os.getenv('BACKEND_URL') + '/threads/' + args.thread_id
    api("get", args, url)


def delete_thread(args):
    logging.debug("Deleting thread")
    url = os.getenv('BACKEND_URL') + '/threads/' + args.thread_id
    api("delete", args, url)


def api(method, args, url, **kwargs):
    login_or_refresh_token(args)
    tokens = read_tokens(args.token_file)
    headers = {'Authorization': f'Bearer {tokens["id_token"]}'}
    authorization_header = {'Authorization': f'Bearer {tokens["id_token"]}'}
    if 'headers' in kwargs:
        kwargs['headers'].update(authorization_header)
    else:
        kwargs['headers'] = authorization_header
    response = requests.request(method, url, **kwargs)
    logging.debug(f'Status: {response.status_code}')
    logging.debug(f'Headers: {response.headers}')
    logging.debug(f'Data:')
    logging.debug(json.dumps(response.json(), indent=4))
    return response


def add_api_command(api):
    user = api.add_parser("get-user", help="Get user info")
    user.set_defaults(func=get_user)

    get_uploads_parser = api.add_parser("get-uploads", help="List uploads")
    get_uploads_parser.set_defaults(func=get_uploads)

    get_uploads_file_parser = api.add_parser("get-uploads-file", help="Print content content")
    add_prefix_arg(get_uploads_file_parser)
    get_uploads_file_parser.set_defaults(func=get_uploads_file)

    post_uploads_file_parser = api.add_parser("post-uploads-file", help="Upload file using API")
    add_name_arg(post_uploads_file_parser)
    add_file_arg(post_uploads_file_parser)
    post_uploads_file_parser.set_defaults(func=post_uploads_file)

    put_uploads_file_parser = api.add_parser("put-uploads-file", help="Upload file using S3")
    add_name_arg(put_uploads_file_parser)
    add_file_arg(put_uploads_file_parser)
    put_uploads_file_parser.set_defaults(func=put_uploads_file)

    delete_uploads_file_parser = api.add_parser("delete-uploads-file", help="Delete uploads file")
    add_prefix_arg(delete_uploads_file_parser)
    delete_uploads_file_parser.set_defaults(func=delete_uploads_file)

    post_index_file_parser = api.add_parser("post-index-file", help="Index an upload into a collection")
    add_collection_arg(post_index_file_parser)
    add_prefix_arg(post_index_file_parser)
    post_index_file_parser.set_defaults(func=post_index_file)

    post_index_parser = api.add_parser("post-index", help="Post index")
    add_collection_arg(post_index_parser)
    post_index_parser.add_argument("query", type=str, help="Query string")
    post_index_parser.add_argument("-p", "--parent-id", help="Parent Message ID of this message")
    post_index_parser.set_defaults(func=post_index)

    get_index_parser = api.add_parser("get-index", help="List collections")
    get_index_parser.set_defaults(func=get_index)

    delete_index_parser = api.add_parser("delete-index", help="Delete a collection")
    add_collection_arg(delete_index_parser)
    delete_index_parser.set_defaults(func=delete_index)

    get_threads_parser = api.add_parser("get-threads", help="Get threads")
    get_threads_parser.set_defaults(func=get_threads)

    get_thread_messages_parser = api.add_parser("get-thread-messages", help="Get thread messages")
    add_thread_arg(get_thread_messages_parser)
    get_thread_messages_parser.set_defaults(func=get_thread_messages)

    delete_thread_parser = api.add_parser("delete-thread", help="Delete thread")
    add_thread_arg(delete_thread_parser)
    delete_thread_parser.set_defaults(func=delete_thread)

    return {}  # no subcommands
