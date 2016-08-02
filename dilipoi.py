#!/usr/bin/env python3

# http://stackoverflow.com/questions/16867347/step-by-step-debugging-with-ipython
# import ipdb; ipdb.set_trace()

import sys
if sys.version_info < (3, 0):
    sys.stderr.write('ERROR: Python 3.0 or newer version is required.\n')
    sys.exit(1)
import argparse
import requests
import urllib
import json
import re
import logging
import subprocess
import xml.etree.ElementTree as ET

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
FLASH_HEADER = 'ShockwaveFlash/22.0.0.209'

DILIDILI_DOMAIN_NAME = 'www.dilidili.com'
DILIDILI_BASE_URL = "http://{0}".format(DILIDILI_DOMAIN_NAME)
DILIDILI_VEDIO_URL_FORMAT = DILIDILI_BASE_URL + "/{0}/"

CK_PLAYER_DOMAIN_NAME = 'player.xcmh.cc:60000'
CK_PLAYER_BASE_URL = 'https://{0}'.format(CK_PLAYER_DOMAIN_NAME)

# {"letvcloud":3,"bilibili":3,"youku":3}
COOKIE_HD = '%7B%22letvcloud%22%3A3%2C%22bilibili%22%3A3%2C%22youku%22%3A3%7D'

class DiliPoi(object):
    def __init__(self, dili_video_path):
        self.dili_video_url = DILIDILI_VEDIO_URL_FORMAT.format(dili_video_path)

    def play(self):
        iframe_url, video_title = self.extract_iframe_url()
        parse_url, video_type = self.extract_parse_url_from_iframe_html_content(iframe_url)
        video_urls = None

        if video_type == 'yun':
            video_urls = self.fetch_m3u8_playlist(iframe_url, parse_url)
        else:
            video_urls = self.fetch_xml_playlist_and_extract_videos(iframe_url, parse_url)
        #else:
        #    raise Exception('Not implemented for video type: {0}'.format(video_type))
        
        self.launch_mpv(video_type, video_title, video_urls)

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

        response = requests.get(self.dili_video_url, headers=headers)
        response.encoding = 'utf-8'
        response_body = response.text
        
        # Extract title
        regex = re.compile(r'<title>(.+)</title>')
        regex_match = regex.search(response_body)
        video_title = regex_match.group(1)
        logging.info('Extracted title: {0}'.format(video_title))

        # Extract iframe URL
        regex = re.compile(r'<iframe.*src="([^"]+)"[^>]*></iframe>')
        regex_match = regex.search(response_body)
        iframe_url = regex_match.group(1)
        logging.debug('iframe_url: {0}'.format(iframe_url))
        return (iframe_url, video_title)

    def extract_parse_url_from_iframe_html_content(self, iframe_url):
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

        response = requests.get(iframe_url, headers=headers)
        response_body = response.text
        #logging.debug('iframe html content: {0}'.format(response_body))
        
        vid_regex = re.compile(r'var\s+vid="([^"]+)"')
        vid_regex_match = vid_regex.search(response_body)
        vid = vid_regex_match.group(1)
        logging.debug('vid: {0}'.format(vid))

        vtype_regex = re.compile(r'var\s+typ="([^"]+)"')
        vtype_regex_match = vtype_regex.search(response_body)
        vtype = vtype_regex_match.group(1)
        logging.debug('type: {0}'.format(vtype))

        sign_regex = re.compile(r'var\s+sign="([^"]+)"')
        sign_regex_match = sign_regex.search(response_body)
        sign = sign_regex_match.group(1)
        logging.debug('sign: {0}'.format(sign))

        ulk_regex = re.compile(r'var\s+ulk="([^"]+)"')
        ulk_regex_match = ulk_regex.search(response_body)
        ulk = None

        if ulk_regex_match != None:
            ulk = ulk_regex_match.group(1)
            logging.debug('ulk: {0}'.format(ulk))

        raw_parse_url_regex = re.compile(r'url=\'(/parse\.php\?.*tmsign=([\w|\d]+))\'.*;')
        raw_parse_url_regex_match = raw_parse_url_regex.search(response_body)
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

        if vtype == 'yun':
            parse_url = parse_url + '&lm=1'

        logging.debug('parse_url: {0}'.format(parse_url))
        return (parse_url, vtype)

    def fetch_xml_playlist_and_extract_videos(self, iframe_url, parse_url):
        headers = {
            'Host': CK_PLAYER_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'X-Requested-With': FLASH_HEADER,
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
            'Referer': iframe_url,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        response = requests.get(parse_url, headers=headers)
        response_body = response.text
        logging.debug('Playlist content: {0}'.format(response_body))
        playlist_xml_tree = ET.fromstring(response_body)
        video_urls = []

        for video_element in playlist_xml_tree.findall(".//video"):
            video_url = video_element.find("./file").text
            logging.debug('Video url: {0}'.format(video_url))
            video_urls.append(video_url)

        return video_urls

    def fetch_m3u8_playlist(self, iframe_url, parse_url, expose_playlist=False):
        """
        For some videos, a m3u8 playlist will be returned after 2 redirects.
        Exposing playlist may result in bad playing experience since files
        in playlist might have a extreme short duration (e.g. 2s).
        """
        headers = {
            'Host': CK_PLAYER_DOMAIN_NAME,
            'Connection': 'keep-alive',
            'X-Requested-With': FLASH_HEADER,
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
            'Referer': iframe_url,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        # For history and redirection, refer to:
        # http://docs.python-requests.org/en/master/user/quickstart/#redirection-and-history
        response = requests.get(parse_url, headers=headers)
        playlist_content_url = response.url
        logging.debug('Playlist url: {0}'.format(playlist_content_url))

        if expose_playlist:
            return self.expose_m3u8_playlist(playlist_content_url)
        else:
            return playlist_content_url

    def expose_m3u8_playlist(self, playlist_content_url):
        url_obj = urllib.parse.urlparse(playlist_content_url)
        logging.debug('Playlist url host: {0}'.format(url_obj.netloc))

        playlist_content_request_headers = {
            'Host': url_obj.netloc,
            'Connection': 'keep-alive',
            'X-Requested-With': FLASH_HEADER,
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'
        }

        response = requests.get(playlist_content_url, headers=playlist_content_request_headers)
        playlist_content = response.text
        
        video_urls = []
        playlist_lines = playlist_content.splitlines()

        for line in playlist_lines:
            if not line.startswith('#'):
                #logging.debug('Playlist item: {0}'.format(line))
                video_urls.append(line)

        return video_urls

    def launch_mpv(self, video_type, video_title, video_urls):
        command_line = ['mpv', '--http-header-fields', 'User-Agent: ' + USER_AGENT]
        command_line += ['--force-media-title', video_title]
        command_line += ['--title', video_title]
        
        if isinstance(video_urls, str):
           command_line.append(video_urls)
        elif isinstance(video_urls, list):
            if len(video_urls) > 1:
                command_line += ['--merge-files']
            command_line += ['--']
            command_line += video_urls
        else:
            raise Exception('Not implemented for video urls of type: {0}'.format(
                type(video_urls).__name__))

        log_command(command_line)
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

def log_command(command_line):
    '''Log the command line to be executed, escaping correctly
    '''
    logging.debug('Executing: '+' '.join('\''+i+'\'' if ' ' in i or '?' in i or '&' in i or '"' in i else i for i in command_line))

class MyArgumentFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        '''Patch the default argparse.HelpFormatter so that '\\n' is correctly handled
        '''
        return [i for line in text.splitlines() for i in argparse.HelpFormatter._split_lines(self, line, width)]

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    parser = argparse.ArgumentParser(formatter_class=MyArgumentFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help='Print more debugging information')
    parser.add_argument('url', metavar='URL', help='Dilidili video page URL (http://www.dilidili.com/watch*/**/)')
    args = parser.parse_args()
    raw_dili_video_url = args.url
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if args.verbose else logging.INFO)
    dili_video_path_regex = re.compile(r'[http://]*[www\.]*dilidili\.com/(watch\d*/[\d]+)')
    dili_video_path_regex_match = dili_video_path_regex.search(raw_dili_video_url)
    dili_video_path = None

    if dili_video_path_regex_match != None:
        dili_video_path = dili_video_path_regex_match.group(1)
        logging.debug('Video path: {0}'.format(dili_video_path))
        DiliPoi(dili_video_path).play()
    else:
        raise Exception('Malformed video url: {0}'.format(raw_dili_video_url))
