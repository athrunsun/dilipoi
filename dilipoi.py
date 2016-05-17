#!/usr/bin/env python3

# http://stackoverflow.com/questions/16867347/step-by-step-debugging-with-ipython
# import ipdb; ipdb.set_trace()

import sys
if sys.version_info < (3, 0):
    sys.stderr.write('ERROR: Python 3.0 or newer version is required.\n')
    sys.exit(1)
#import argparse
import requests
import json
import re
import logging
import subprocess
import xml.etree.ElementTree as ET

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/47.0.2526.106 Chrome/47.0.2526.106 Safari/537.36'
FLASH_HEADER = 'ShockwaveFlash/11.2.999.999'

DILIDILI_DOMAIN_NAME = 'www.dilidili.com'
DILIDILI_BASE_URL = "http://{0}".format(DILIDILI_DOMAIN_NAME)
DILIDILI_VEDIO_URL_FORMAT = DILIDILI_BASE_URL + "/{0}/"

CK_PLAYER_DOMAIN_NAME = 'player.005.tv:60000'
CK_PLAYER_BASE_URL = 'https://{0}'.format(CK_PLAYER_DOMAIN_NAME)

# {"letvcloud":3,"bilibili":3,"youku":3}
COOKIE_HD = '%7B%22letvcloud%22%3A3%2C%22bilibili%22%3A3%2C%22youku%22%3A3%7D'

class DiliPlay(object):
    def __init__(self, dili_video_path):
        self.dili_video_url = DILIDILI_VEDIO_URL_FORMAT.format(dili_video_path)
        self.video_urls = []
        self.video_title = None

    def play(self):
        self.extract_iframe_url()
        self.fetch_ckplayer_playlist_and_extract_videos(self.extract_parse_url_from_iframe_html_content())
        self.launch_mpv()

    def extract_iframe_url(self):
        headers = {
            'User-Agent': USER_AGENT, 
            'Referer': DILIDILI_BASE_URL, 
            'Host': DILIDILI_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        r = requests.get(self.dili_video_url, headers=headers)
        r.encoding = 'utf-8'
        
        # Extract title
        regex = re.compile(r'<title>(.+)</title>')
        regex_match = regex.search(r.text)
        self.video_title = regex_match.group(1)
        logging.info('Extracted title: {0}'.format(self.video_title))

        # Extract iframe URL
        regex = re.compile(r'<iframe.*src="([^"]+)"[^>]*></iframe>')
        regex_match = regex.search(r.text)
        iframe_url = regex_match.group(1)
        logging.debug('iframe_url: {0}'.format(iframe_url))
        self.iframe_url = iframe_url
        return iframe_url

    def extract_parse_url_from_iframe_html_content(self):
        headers = {
            'User-Agent': USER_AGENT, 
            'Referer': self.dili_video_url, 
            'Host': CK_PLAYER_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cookie': 'hd=' + COOKIE_HD
        }

        r = requests.get(self.iframe_url, headers = headers)
        logging.debug('iframe html content: {0}'.format(r.text))
        
        vid_regex = re.compile(r'var\s+vid="([^"]+)"')
        vid_regex_match = vid_regex.search(r.text)
        vid = vid_regex_match.group(1)
        logging.debug('vid: {0}'.format(vid))

        vtype_regex = re.compile(r'var\s+typ="([^"]+)"')
        vtype_regex_match = vtype_regex.search(r.text)
        vtype = vtype_regex_match.group(1)
        logging.debug('type: {0}'.format(vtype))

        sign_regex = re.compile(r'var\s+sign="([^"]+)"')
        sign_regex_match = sign_regex.search(r.text)
        sign = sign_regex_match.group(1)
        logging.debug('sign: {0}'.format(sign))

        ulk_regex = re.compile(r'var\s+ulk="([^"]+)"')
        ulk_regex_match = ulk_regex.search(r.text)
        ulk = None

        if ulk_regex_match != None:
            ulk = ulk_regex_match.group(1)
            logging.debug('ulk: {0}'.format(ulk))

        raw_parse_url_regex = re.compile(r'url=\'(/parse\.php\?.*tmsign=([\w|\d]+))\'.*;')
        raw_parse_url_regex_match = raw_parse_url_regex.search(r.text)
        raw_parse_url = raw_parse_url_regex_match.group(1)
        tmsign = raw_parse_url_regex_match.group(2)
        logging.debug('raw_parse_url: {0}'.format(raw_parse_url))
        logging.debug('tmsign: {0}'.format(tmsign))

        parse_url = "{ck_base_url}/parse.php?xmlurl=null&type={arg_type}&vid={arg_vid}&hd=3&sign={arg_sign}&tmsign={arg_tmsign}".format(\
            ck_base_url = CK_PLAYER_BASE_URL,\
            arg_type = vtype,\
            arg_vid = vid,\
            arg_sign = sign,\
            arg_tmsign = tmsign)

        if ulk != None:
            parse_url = parse_url + '&userlink=' + ulk

        logging.debug('parse_url: {0}'.format(parse_url))
        return parse_url

    def fetch_ckplayer_playlist_and_extract_videos(self, parse_url):
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
        logging.debug('Playlist content: {0}'.format(r.text))
        playlist_xml_tree = ET.fromstring(r.text)

        for video_element in playlist_xml_tree.findall(".//video"):
            video_url = video_element.find("./file").text
            logging.debug('video_url: {0}'.format(video_url))
            self.video_urls.append(video_url)

    def launch_mpv(self):
        command_line = ['mpv', '--http-header-fields', 'User-Agent: ' + USER_AGENT]
        command_line += ['--force-media-title', self.video_title]

        if len(self.video_urls) > 1:
            command_line += ['--merge-files']

        command_line += ['--']
        command_line += self.video_urls
        player_process = subprocess.Popen(command_line)

        try:
            player_process.wait()
        except KeyboardInterrupt:
            logging.info('Terminating media player...')
            try:
                player_process.terminate()
                try:
                    player_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    logging.info('Killing media player by force...')
                    player_process.kill()
            except Exception:
                pass
            raise
        
        return player_process.returncode

class MyArgumentFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        '''Patch the default argparse.HelpFormatter so that '\\n' is correctly handled
        '''
        return [i for line in text.splitlines() for i in argparse.HelpFormatter._split_lines(self, line, width)]

if __name__ == '__main__':
    #[print(arg) for arg in sys.argv]
    parser = argparse.ArgumentParser(formatter_class=MyArgumentFormatter)
    parser.add_argument('-d', '--debug', action='store_true', help='Stop execution immediately when an error occures')
    raw_dili_video_url = sys.argv[1]
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if args.verbose else logging.INFO)
    dili_video_path_regex = re.compile(r'[http://]*[www\.]*dilidili\.com/(watch\d*/[\d]+)')
    dili_video_path_regex_match = dili_video_path_regex.search(raw_dili_video_url)
    dili_video_path = None

    if dili_video_path_regex_match != None:
        dili_video_path = dili_video_path_regex_match.group(1)
        logging.debug('Video path: {0}'.format(dili_video_path))
        DiliPlay(dili_video_path).play()
    else:
        raise Exception('Wrong video url format: {0}'.format(raw_dili_video_url))
