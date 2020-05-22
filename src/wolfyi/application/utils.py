def normalize_url_input(url):
    url = url.lstrip()
    if '://' not in url:
        url = 'http://' + url
    return url
