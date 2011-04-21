'''
Created on 2011/04/21

@author: gollerjo
'''

from HTMLParser import HTMLParser
# from HTMLParser import HTMLParseError
import re

class HtmlLangid(HTMLParser):
    '''
    Analyzes the meta data of an HTML document to extract
    information about its language and character encoding.
    '''

    def __init__(self):
        HTMLParser.__init__(self)
        self._encoding_pattern = re.compile('charset\s*=\s*([^\s\x22\x27]+)')
        self._script_pattern   = re.compile('(?:<script[^>]*/\s*>|<script[^>]*>.*?</script>)',
                                            re.IGNORECASE)
        self.reset()

    def reset(self):
        HTMLParser.reset(self)
        self._result_language = ''
        self._result_encoding = ''

    def feed(self,contents):
        contents = self._script_pattern.sub('',contents)
        HTMLParser.feed(self,contents)

    def handle_starttag(self,tag,attrs):
        if tag == 'meta':
            http_equiv = ''
            content    = ''
            for (key,val) in attrs:
                if key == 'http-equiv':
                    http_equiv = val
                elif key == 'content':
                    content = val
            if http_equiv == 'content-language':
                self._result_language = content
            elif http_equiv == 'content-type':
                m = self._encoding_pattern.search(content)
                if m:
                    self._result_encoding = m.group(1)
