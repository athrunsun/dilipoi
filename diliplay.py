# http://stackoverflow.com/questions/16867347/step-by-step-debugging-with-ipython
# import ipdb; ipdb.set_trace()

import requests
import json
import re

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
DILIDILI_DOMAIN_NAME = 'www.dilidili.com'
DILIDILI_BASE_URL = "http://{0}/".format(DILIDILI_DOMAIN_NAME)
DILIDILI_VEDIO_URL_FORMAT = DILIDILI_BASE_URL + "watch/{0}/"

TV_PLAYER_DOMAIN_NAME = 'player.005.tv:60000'

# {"letvcloud":3,"bilibili":3,"youku":3}
COOKIE_HD = '%7B%22letvcloud%22%3A3%2C%22bilibili%22%3A3%2C%22youku%22%3A3%7D'

class DiliPlay(object):
    def __init__(self, vid):
        self.vedio_url = DILIDILI_VEDIO_URL_FORMAT.format(vid)

    def extract_iframe_url(self):
        headers = {
            'User-Agent': USER_AGENT, 
            'Referer': DILIDILI_BASE_URL, 
            'Host': DILIDILI_DOMAIN_NAME
        }

        r = requests.get(self.vedio_url, headers = headers)
        regex = re.compile(r'<iframe.*src="([^"]+)"[^>]*></iframe>')
        regex_match = regex.search(r.text)
        return regex_match.group(1)

    def extract_parse_url_from_iframe_html_content(self, iframe_url):
        headers = {
            'User-Agent': USER_AGENT, 
            'Referer': self.vedio_url, 
            'Host': TV_PLAYER_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        r = requests.get(iframe_url, headers = headers)
        print(r.text)

if __name__ == '__main__':
    diliplay = DiliPlay(26780)
    diliplay.extract_parse_url_from_iframe_html_content(diliplay.extract_iframe_url())