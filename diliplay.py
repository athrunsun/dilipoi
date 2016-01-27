# http://stackoverflow.com/questions/16867347/step-by-step-debugging-with-ipython
# import ipdb; ipdb.set_trace()

import requests
import json
import re
from lxml import etree

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/47.0.2526.106 Chrome/47.0.2526.106 Safari/537.36'
FLASH_HEADER = 'ShockwaveFlash/11.2.999.999'

DILIDILI_DOMAIN_NAME = 'www.dilidili.com'
DILIDILI_BASE_URL = "http://{0}".format(DILIDILI_DOMAIN_NAME)
DILIDILI_VEDIO_URL_FORMAT = DILIDILI_BASE_URL + "/watch/{0}/"

CK_PLAYER_DOMAIN_NAME = 'player.005.tv:60000'
CK_PLAYER_BASE_URL = 'https://{0}'.format(CK_PLAYER_DOMAIN_NAME)

# {"letvcloud":3,"bilibili":3,"youku":3}
COOKIE_HD = '%7B%22letvcloud%22%3A3%2C%22bilibili%22%3A3%2C%22youku%22%3A3%7D'

class DiliPlay(object):
    def __init__(self, dili_video_id):
        self.vedio_url = DILIDILI_VEDIO_URL_FORMAT.format(dili_video_id)

    def play(self):
        self.extract_iframe_url()
        self.fetch_ckplayer_playlist(self.extract_parse_url_from_iframe_html_content())

    def extract_iframe_url(self):
        headers = {
            'User-Agent': USER_AGENT, 
            'Referer': DILIDILI_BASE_URL, 
            'Host': DILIDILI_DOMAIN_NAME
        }

        r = requests.get(self.vedio_url, headers = headers)
        regex = re.compile(r'<iframe.*src="([^"]+)"[^>]*></iframe>')
        regex_match = regex.search(r.text)
        iframe_url = regex_match.group(1)
        print("iframe_url:" + iframe_url)
        self.iframe_url = iframe_url
        return iframe_url

    def extract_parse_url_from_iframe_html_content(self):
        headers = {
            'User-Agent': USER_AGENT, 
            'Referer': self.vedio_url, 
            'Host': CK_PLAYER_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        r = requests.get(self.iframe_url, headers = headers)
        #print(r.text)
        
        vid_regex = re.compile(r'var\s+vid="([^"]+)"')
        vid_regex_match = vid_regex.search(r.text)
        vid = vid_regex_match.group(1)
        print("vid:" + vid)

        vtype_regex = re.compile(r'var\s+typ="([^"]+)"')
        vtype_regex_match = vtype_regex.search(r.text)
        vtype = vtype_regex_match.group(1)
        print("type:" + vtype)

        sign_regex = re.compile(r'var\s+sign="([^"]+)"')
        sign_regex_match = sign_regex.search(r.text)
        sign = sign_regex_match.group(1)
        print("sign:" + sign)

        raw_parse_url_regex = re.compile(r'url=\'(/parse\.php\?.*tmsign=([\w|\d]+))\';')
        raw_parse_url_regex_match = raw_parse_url_regex.search(r.text)
        raw_parse_url = raw_parse_url_regex_match.group(1)
        tmsign = raw_parse_url_regex_match.group(2)
        print("raw_parse_url:" + raw_parse_url)
        print("tmsign:" + tmsign)

        parse_url = "{ck_base_url}/parse.php?xmlurl=null&type={arg_type}&vid={arg_vid}&hd=3&sign={arg_sign}&tmsign={arg_tmsign}".format(\
            ck_base_url = CK_PLAYER_BASE_URL,\
            arg_type = vtype,\
            arg_vid = vid,\
            arg_sign = sign,\
            arg_tmsign = tmsign)

        print("parse_url:" + parse_url)

        return parse_url

    def fetch_ckplayer_playlist(self, parse_url):
        headers = {
            'Host': CK_PLAYER_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'X-Requested-With': FLASH_HEADER,
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
            'Referer': self.iframe_url,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        r = requests.get(parse_url, headers = headers)
        print(r.text)
        playlist_xml_tree = etree.fromstring(r.text)

        for video_element in playlist_xml_tree.findall(".//video"):
            video_url = video_element.find("./file").text
            print("video_url:" + video_url)

if __name__ == '__main__':
    diliplay = DiliPlay(27613)
    diliplay.play()