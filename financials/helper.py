"""
    financials.helper
    =================

    Misc helper functions.

    copyright: (c) 2017 by Maris Jensen and Ivo Welch.
    license: BSD, see LICENSE for more details.
"""
import time
from collections import Counter
from functools import wraps
try:
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, URLError, HTTPError

def clean_ticker(dirty):
    """Returns standardized ticker.

    :param dirty: raw text
    """
    if not dirty:
        return None

    _dirty = dirty.upper().replace('"', '').strip()
    
    if _dirty.startswith('(') and _dirty.endswith(')'):
        _dirty = _dirty.replace('(', '').replace(')', '')
    elif _dirty.startswith('[') and _dirty.endswith(']'):
        _dirty = _dirty.replace('[', '').replace(']', '')

    mess = ('OTCBB', 'NYSE', 'AMEX', 'OB', 'PK', 'OTCQB', 'OTBB', 'OTC', 'TSX', 
            'US', 'NASDQ', 'NASDAQ', 'NASD', 'NSYE', 'OTCQX')
    if any(x.strip() in mess for x in _dirty.split(':')):
        _dirty = ''.join([x.strip() for x in _dirty.split(':')
                          if x.strip() not in mess])

    if any(x.strip() in mess for x in _dirty.split('-')):
        _dirty = '-'.join([x.strip() for x in _dirty.split('-')
                          if x.strip() not in mess])

    if any(x.strip() in mess for x in _dirty.split('/')):
        _dirty = ''.join([x.strip() for x in _dirty.split('/')
                          if x.strip() not in mess])
        
    if _dirty.endswith('-'):
        _dirty = _dirty[:-1]

    _dirty = _dirty.split('.')[0].split('(')[0].split(')')[0].split(',')[0]

    if _dirty.rfind('$') != -1 or _dirty.rfind('_') != -1:
        return None
    if not any(c.isalpha() for c in _dirty):
        return None
    if len(Counter(x for x in _dirty.replace(' ', ''))) == 1 and \
                _dirty.rfind('X') != -1:
        return None
    miss = ('NONE', 'N/A', 'NA', 'UNKNOWN', 'COME', 'SEE', 'TRADED',
            'TICKER', 'NO', 'FOR', 'FOOTNOTE', 'REMARK', 'SYMBOL', 'NOT')
    if ''.join([a for a in _dirty if a.isalpha()]) in miss:
        return None

    if len(_dirty.split()) > 1:
        if len([x for x in _dirty.split() if x in miss]) > 0:
            return None
        else:
            _dirty = '/'.join([a for a in _dirty.split() if a not in mess])
    if any(c.isalpha() for c in _dirty.split('-')[0].split('/')[0]):
        _dirty = _dirty.split('-')[0].split('/')[0]
    return ''.join([a for a in _dirty if a.isalnum()])


def format_zip(field):
    """Return str version of 5 digit zip. Examples:

        format_zip('08544-4320') >>> '08544'
        format_zip('085444320') >>> '08544'
        format_zip(85444320) >>> '08544'
        format_zip(851) >>> '00851'

    :param field: raw text
    """
    if field is None or not field:
        return None
    field = str(field).split('-')[0].split(' ')[0].split('.')[0]
    if len(field) <= 5:
        return field.zfill(5) if field.isdigit() else None
    elif len(field) <= 9:
        field = field.zfill(9)[:5]
        return field if field.isdigit() else None
    return None
 

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    """Retries the decorated function.
    
    copyright: (c) 2013, SaltyCrane.
    license: BSD, see github.com/saltycrane/retry-decorator for details.
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry


@retry((URLError, HTTPError), tries=5, delay=3, backoff=2)
def openurl(url):
    """Retries urlopen.

    :param url: url to open 
    """
    return urlopen(url)

