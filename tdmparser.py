""" tdmparser.py

   
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have read a copy of the GNU General Public License.
    If not, see <https://www.gnu.org/licenses/>.

    ===============================================================

    This program, written by Claudio Tubertini, Bologna, 2021, is largely inspired 
    by urllib.robotparser and by scrapy/protego. It implements the 
    TDM Reservation Protocol (TDMRep), 
    Draft Community Group Report of 05 October 2021
    https://w3c.github.io/tdm-reservation-protocol/spec/
    ================================================================
"""

import collections
import urllib.parse
import urllib.request
import json
import re
import logging
from lxml import html

__all__ = ["TDMParser"]

logger = logging.getLogger(__name__)

_WILDCARDS = {'*', '$'}

_HEX_DIGITS = set('0123456789ABCDEFabcdef')

class TDMParser:
    """This class checks the presence of one of the three rules of TDM proposal.
    And executes the available rule in order of preference"""

    def __init__(self, url=''):
        # self.disallow_all = False
        self.allow_all = False
    
    def check(self, url):
        parsed = urllib.parse.urlparse(path)
        ############### TODO
        if parsed.path != '/.well-known/tdmrep.json':
            pass
        
        


class TDMFileParser:
    """ This class provides a set of methods to read, parse and answer
    questions about a single file named tdmrep.json, hosted in the /.well-known 
    repository of a Web server.
    """

    def __init__(self, url=''):
        self.entries = []
        self.set_url(url)
        self.last_checked = 0

    def mtime(self):
        """Returns the time the tdmrep.json file was last fetched.
        This is useful for long-running web spiders that need to
        check for new tdmrep.json files periodically.
        """
        return self.last_checked

    def modified(self):
        """Sets the time the tdmrep.json file was last fetched to the
        current time.
        """
        import datetime
        self.last_checked = datetime.datetime.now(tz=None)

    def set_url(self, url):
        """Sets the URL referring to a tdmrep.json file."""
        self.url = url
        self.host, self.path = urllib.parse.urlparse(url)[1:3]

    def read(self):
        """Reads the tdmrep.json URL and feeds it to the parser."""
        try:
            f = urllib.request.urlopen(self.url)
        except urllib.error.HTTPError as err:
            #self.allow_all = True
            print(err)
        else:
            raw = json.loads(f.read())
            self.parse(raw)

    def parse(self, raws):
        """Parse the input objects from a tdmrep.json file.
        """
        self.modified()
        for raw in raws:
            item = Entry(raw)
            self.entries.append(item)

    def can_fetch(self, url):
        """using the parsed tdmrep.json decide if you can fetch url"""
        parsed_url = urllib.parse.urlparse(urllib.parse.unquote(url))
        url = urllib.parse.urlunparse(('','',parsed_url.path,
            parsed_url.params,parsed_url.query, parsed_url.fragment))
        url = urllib.parse.quote(url)
        if not url:
            url = "/"
        fetch = []
        for entry in self.entries:
            if entry.allowance(url):
                return entry.allowance(url)
        #     allow = entry.allowance(url)
        #     path = entry.location 
        #     fetch.append((path, allow))
        # return fetch

    def __str__(self):
        entries = self.entries
        #return json.dumps(entries)
        return '\n\n'.join(map(str, entries))


class TDMHeader:
    """ This class retrieves the headers relevant to text and data mining."""

    def __init__(self, path):
        path = urllib.parse.urlunparse(urllib.parse.urlparse(path))
        self.path = urllib.parse.quote(path)

    def _get_headers(self):
        with urllib.request.urlopen(self.path) as response:
            the_page = response.getheaders()
        ret = {k:v for k,v in the_page}
        #ret = (res.get('tdm-reservation',''), res.get('tdm-policy',''))
        return ret

    def is_allowed(self):
        ret = self._get_headers()
        if ret['tdm-reservation'] == 0:
            return True
        elif ret['tdm-reservation'] == 1:
            if ret['tdm-policy']:
                return ret['tdm-policy']
            else:
                return False
        return None

    def __str__(self):
        if self.is_allowed():
            ret = self.path + 'can be freely mined.'
        elif self._get_headers()['tdm-reservation'] == 1:
            ret = self.path + 'cannot be freely mined'
            if self._get_headers()['tdm-policy']:
               ret = ret + f' but you can read a policy: {self._get_headers()['tdm-policy']}.'
        return ret


class TDMhtmlHead:
    """ This class retrieves TDM Metadata in HTML Content relevant to text and data mining."""

    def __init__(self, path):
        path = urllib.parse.urlunparse(urllib.parse.urlparse(path))
        self.path = urllib.parse.quote(path)

    def _get_head(self):
        ret = {}
        with urllib.request.urlopen(self.path) as response:
            the_page = response.read()
        tree = html.fromstring(the_page)
        metadata = tree.xpath('//head/meta')
        for m in metadata:
            k = ''.join(m.xpath('./@name'))
            v = ''.join(m.xpath('./@content'))
            ret[k] = v
        return ret

    def is_allowed(self):
        ret = self._get_head()
        if ret['tdm-reservation'] == 0:
            return True
        elif ret['tdm-reservation'] == 1:
            if ret['tdm-policy']:
                return ret['tdm-policy']
            else:
                return False
        return None

    def __str__(self):
        if self.is_allowed():
            ret = self.path + 'can be freely mined.'
        elif self._get_head()['tdm-reservation'] == 1:
            ret = self.path + 'cannot be freely mined'
            if self._get_head()['tdm-policy']:
               ret = ret + f' but you can read a policy: {self._get_head()['tdm-policy']}.'
        return ret


class Entry:
    """
    A tdmrep.json file contains an array of JSON objects; each object represents 
    a rule and contains three properties:
        - location: a pattern matching the path of a set of files hosted on the server, associated with the sibling TDM properties.
        - tdm-reservation: a TDM reservation value associated with the current pattern.
        - tdm-policy: a TDM Policy value associated with the current pattern.
    Each entry in this class represents an object."""

    def __init__(self, obj):
        self.location = obj.get('location','')
        self.tdm_reservation = obj.get('tdm-reservation','')
        self.tdm_policy = obj.get('tdm-policy','')
        path = urllib.parse.urlunparse(urllib.parse.urlparse(self.location))
        self.path = urllib.parse.quote(path)

    def __str__(self):
        if self.tdm_reservation == 0:
            ret = self.location + ' can be freely mined.'
        elif self.tdm_reservation == 1:
            ret = self.location + ' cannot be freely mined'
            if self.tdm_policy:
               ret = ret + f' but you can read a policy: {self.tdm_policy}.'
        return ret

    def allowance(self, filename):
        m = _URLPattern(self.location)
        if m.match(filename):
            if self.tdm_reservation == 0:
                return True
            if self.tdm_reservation == 1 and self.tdm_policy:
                return self.tdm_policy
            if self.tdm_reservation == 1 and not self.tdm_policy:
                return False
        # else:
        #     print("Check the file name!!")


class _URLPattern(object):
    """Internal class which represents a URL pattern."""

    def __init__(self, pattern):
        self._pattern = pattern
        self.priority = len(pattern)
        self._contains_asterisk = '*' in self._pattern
        self._contains_dollar = self._pattern.endswith('$')

        if self._contains_asterisk:
            self._pattern_before_asterisk = self._pattern[:self._pattern.find('*')]
        elif self._contains_dollar:
            self._pattern_before_dollar = self._pattern[:-1]

        self._pattern_compiled = False

    def match(self, url):
        """Return True if pattern matches the given URL, otherwise return False."""
        # check if pattern is already compiled
        if self._pattern_compiled:
            return self._pattern.match(url)

        if not self._contains_asterisk:
            if not self._contains_dollar:
                # answer directly for patterns without wildcards
                return url.startswith(self._pattern)

            # pattern only contains $ wildcard.
            return url == self._pattern_before_dollar

        if not url.startswith(self._pattern_before_asterisk):
            return False

        self._pattern = self._prepare_pattern_for_regex(self._pattern)
        self._pattern = re.compile(self._pattern)
        self._pattern_compiled = True
        return self._pattern.match(url)

    def _prepare_pattern_for_regex(self, pattern):
        """Return equivalent regex pattern for the given URL pattern."""
        pattern = re.sub(r'\*+', '*', pattern)
        s = re.split(r'(\*|\$$)', pattern)
        for index, substr in enumerate(s):
            if substr not in _WILDCARDS:
                s[index] = re.escape(substr)
            elif s[index] == '*':
                s[index] = '.*?'
        pattern = ''.join(s)
        return pattern

    def _unquote(self, url, ignore='', errors='replace'):
        """Replace %xy escapes by their single-character equivalent."""
        if '%' not in url:
            return url

        def hex_to_byte(h):
            """Replaces a %xx escape with equivalent binary sequence."""
            if six.PY2:
                return chr(int(h, 16))
            return bytes.fromhex(h)

        # ignore contains %xy escapes for characters that are not
        # meant to be converted back.
        ignore = {'{:02X}'.format(ord(c)) for c in ignore}

        parts = url.split('%')
        parts[0] = parts[0].encode('utf-8')

        for i in range(1, len(parts)):
            if len(parts[i]) >= 2:
                # %xy is a valid escape only if x and y are hexadecimal digits.
                if set(parts[i][:2]).issubset(_HEX_DIGITS):
                    # make sure that all %xy escapes are in uppercase.
                    hexcode = parts[i][:2].upper()
                    leftover = parts[i][2:]
                    if hexcode not in ignore:
                        parts[i] = hex_to_byte(hexcode) + leftover.encode('utf-8')
                        continue
                    else:
                        parts[i] = hexcode + leftover

            # add back the '%' we removed during splitting.
            parts[i] = b'%' + parts[i].encode('utf-8')

        return b''.join(parts).decode('utf-8', errors)

    def hexescape(self, char):
        """Escape char as RFC 2396 specifies"""
        hex_repr = hex(ord(char))[2:].upper()
        if len(hex_repr) == 1:
            hex_repr = "0%s" % hex_repr
        return "%" + hex_repr

    def _quote_path(self, path):
        """Return percent encoded path."""
        parts = urlparse(path)
        path = self._unquote(parts.path, ignore='/%')
        # quote do not work with unicode strings in Python 2.7
        if six.PY2:
            path = quote(path.encode('utf-8'), safe='/%')
        else:
            path = quote(path, safe='/%')

        parts = ParseResult('', '', path, parts.params, parts.query, parts.fragment)
        path = urlunparse(parts)
        return path or '/'

    def _quote_pattern(self, pattern):
        # Corner case for query only (e.g. '/abc?') and param only (e.g. '/abc;') URLs.
        # Save the last character otherwise, urlparse will kill it.
        last_char = ''
        if pattern[-1] == '?' or pattern[-1] == ';' or pattern[-1] == '$':
            last_char = pattern[-1]
            pattern = pattern[:-1]

        parts = urlparse(pattern)
        pattern = self._unquote(parts.path, ignore='/*$%')
        # quote do not work with unicode strings in Python 2.7
        if six.PY2:
            pattern = quote(pattern.encode('utf-8'), safe='/*%')
        else:
            pattern = quote(pattern, safe='/*%')

        parts = ParseResult('', '', pattern + last_char, parts.params, parts.query, parts.fragment)
        pattern = urlunparse(parts)
        return pattern
