# https://developers.google.com/youtube/v3/guides/uploading_a_video/
import argparse
import http.client
import json
import logging
import random
import sys
import time
import webbrowser
from pathlib import Path

import httplib2
# noinspection PyUnresolvedReferences
from apiclient.discovery import build
# noinspection PyUnresolvedReferences
from apiclient.errors import HttpError
# noinspection PyUnresolvedReferences
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)

RETRIABLE_STATUS_CODES = {500, 502, 503, 504}

CLIENT_SECRETS_FILE = 'client_secrets.json'

YOUTUBE_UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

MISSING_CLIENT_SECRETS_MESSAGE = f'''\
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   {(Path(__file__).parent / CLIENT_SECRETS_FILE).absolute()}

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets'''

VALID_PRIVACY_STATUSES = ('private', 'public', 'unlisted')


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage(f'{sys.argv[0]}-oauth2.json')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(',')

    body = {'snippet': {'title': options.title,
                        'description': options.description,
                        'tags': tags,
                        'categoryId': options.category},
            'status': {'privacyStatus': options.privacyStatus}}

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def _json_content(content):
    return json.dumps(json.loads(content.decode('UTF-8')), ensure_ascii=False, indent=1)


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logging.info('Uploading file...')
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    id_ = response['id']
                    try:
                        webbrowser.open_new_tab(f'https://youtu.be/{id_}')
                    except webbrowser.Error:
                        pass
                    logging.info(f'Video id {id_!r} was successfully uploaded.')
                else:
                    exit(f'The upload failed with an unexpected response: {response}')
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f'A retriable HTTP error {e.resp.status} occurred:\n{_json_content(e.content)}'
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f'A retriable error occurred: {e}'

        if error is not None:
            logging.error(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            logging.info(f'Sleeping {sleep_seconds:g} seconds and then retrying...')
            time.sleep(sleep_seconds)


def parse_args(args=None):
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument('--auth_host_name', default='localhost',
                           help='Hostname when running a local web server.')
    argparser.add_argument('--noauth_local_webserver', action='store_true',
                           default=False, help='Do not run a local web server.')
    argparser.add_argument('--auth_host_port', default=(8080, 8090), type=int,
                           nargs='*', help='Port web server should listen on.')
    argparser.add_argument(
        '--logging_level', default='ERROR',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        help='Set the logging level of detail.')

    argparser.add_argument('--file', type=Path, required=True, help='Video file to upload')
    argparser.add_argument('--title', help='Video title', default='Untitled')
    argparser.add_argument('--description', help='Video description',
                           default='')
    argparser.add_argument('--category', default='22',
                           help='Numeric video category. ' +
                                'See https://developers.google.com/youtube/v3/docs/videoCategories/list')
    argparser.add_argument('--keywords', help='Video keywords, comma separated',
                           default='')
    argparser.add_argument('--privacy-status', choices=VALID_PRIVACY_STATUSES,
                           default=VALID_PRIVACY_STATUSES[0], help='Video privacy status.', dest='privacyStatus')
    return argparser.parse_args(args)


def upload(args=None):
    args = parse_args(args)
    if not args.file.is_file():
        exit('Please specify a valid file using the --file parameter.')

    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        logging.error(f'An HTTP error {e.resp.status} occurred:\n{_json_content(e.content)}')
