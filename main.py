import functools
import os
from multiprocessing.pool import ThreadPool
from threading import Lock

import requests
import mastodon


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
        s_print(status.id)

        if status.reblog is not None:
            status = status.reblog
            s_print(f'Reblog of {status.id}')

        medias = status.media_attachments
        for media in medias:
            fetch(media.url)
            fetch(media.preview_url)

    @staticmethod
    def fetch(url):
        res = requests.head(url)
        s_print(f'{media.url} {res.reason} {res.headers["CF-Cache-Status"]}')


def stream_thread(target_function, listener):
    s_print(target_function.__name__)
    target_function(listener, reconnect_async=True)

MASTODON_URL=os.getenv('MASTODON_URL')
ACCESS_TOKEN=os.getenv('MASTODON_ACCESS_TOKEN')

api = mastodon.Mastodon(
    api_base_url=MASTODON_URL,
    access_token=ACCESS_TOKEN)

listener = MediaFetcher(api)
streams = [
    api.stream_user,
    api.stream_public,
]
pool = ThreadPool(len(streams))
pool.map(functools.partial(stream_thread, listener=listener), streams)
pool.join()
