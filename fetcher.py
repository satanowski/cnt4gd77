import threading

import logging as log
from requests import get


log.basicConfig(level=log.DEBUG)


EXT_SOURCES = {
    'rep': 'https://przemienniki.net/export/rxf.xml?country=pl&onlyworking',
    'dmr': 'http://dmr.ham-digital.net/user_by_call.php?id=260',
    'kab': 'https://sp5kab.pl/czlonkowie/',
}

HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,"\
                  " like Gecko) Chrome/63.0.3239.84 Safari/537.36",
}

result_lock = threading.Lock()


def fetch(key, url, output):
    resp = get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        log.error("Fetch error (%s): %s", url, resp.status_code)
        with result_lock:
            output[key] = None
        return None
    with result_lock:
        output[key] = resp.content.decode('utf-8')
        log.debug('Got %d bytes for %s', len(resp.content), key)


def fetch_urls() -> list:
    results = {}
    threads = []

    for source in EXT_SOURCES:
        threading.Thread(
            target=fetch,
            args=(source, EXT_SOURCES[source], results)
        ).start()

    for t in threading.enumerate():
        if t != threading.current_thread():
            t.join()

    return results