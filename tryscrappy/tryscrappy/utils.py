from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, parse_qs


def convert_date(date):
    d, m, y = date.split()
    m = {
        'ianuarie': 'January',
        'februarie': 'February',
        'martie': 'March',
        'aprilie': 'April',
        'mai': 'May',
        'iunie': 'June',
        'iulie': 'July',
        'august': 'August',
        'septembrie': 'September',
        'octombrie': 'October',
        'noiembrie': 'November',
        'decembrie': 'December'
    }[m.lower()]

    return datetime.strptime(f'{d} {m} {y}', "%d %B %Y").date()


def clean_url(current_friend_id, *fargs):
    url_parts = list(urlparse(current_friend_id))
    qs = url_parts[4]
    args = parse_qsl(qs)
    args = [(f, v) for f, v in args if f in fargs]
    url_parts[4] = urlencode(args)
    return urlunparse(url_parts)


def compare_url_existing_parameters(url1, url2):
    parse1, parse2 = urlparse(url1), urlparse(url2)
    if parse1.path != parse2.path:
        return False
    qs1, qs2 = parse1.query, parse2.query
    kargs1, kargs2 = parse_qs(qs1), parse_qs(qs2)
    rez = True
    for key, val in kargs1.items():
        if key in kargs2 and kargs2[key] != val:
            rez = False
    return rez
