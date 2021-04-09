import functools
from multiprocessing.pool import ThreadPool
from threading import Lock

import requests
import mastodon

from get_docker_secret import get_docker_secret


s_print_lock = Lock()


def s_print(*args, **kwargs):
    with s_print_lock:
        print(*args, **kwargs)


class MediaFetcher(mastodon.StreamListener):

    def __init__(self, api):
        super().__init__()
        self.api = api
        me = api.account_verify_credentials()
        s_print(f'I am {me.acct}')

    def on_update(self, status):
        s_print(f'{status.id} {len(status.media_attachments)}')

        if status.reblog is not None:
            status = status.reblog
            s_print(f'Reblog of {status.id} {len(status.media_attachments)}')

        medias = status.media_attachments
        if medias:
            s_print(f'Downloading {len(medias)} medias')
        for media in medias:
            self.fetch(media.url)
            self.fetch(media.preview_url)

    @staticmethod
    def fetch(url):
        res = requests.get(url)
        if res.headers.get('Server') == 'cloudflare':
            cache_status = res.headers['CF-Cache-Status']
            ray = res.headers['CF-Ray']
        else:
            cache_status = ''
            ray = ''

        s_print(
            f'{res.url} {res.reason}'
            f' {res.elapsed.total_seconds():.3f}'
            f' {cache_status} {ray}')


def stream_thread(target_function, listener):
    s_print(target_function.__name__)
    target_function(listener, reconnect_async=True)


MASTODON_URL = get_docker_secret('MASTODON_URL')
ACCESS_TOKEN = get_docker_secret('MASTODON_ACCESS_TOKEN')

api = mastodon.Mastodon(
    api_base_url=MASTODON_URL,
    access_token=ACCESS_TOKEN)

listener = MediaFetcher(api)
streams = [
    api.stream_user,
    api.stream_public,
]

while True:
    pool = ThreadPool(len(streams))
    try:
        pool.map(functools.partial(stream_thread, listener=listener), streams)
    except (mastodon.MastodonNetworkError):
        pool.terminate()
        continue
    finally:
        pool.close()
        pool.join()
