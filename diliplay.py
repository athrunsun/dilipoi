# http://stackoverflow.com/questions/16867347/step-by-step-debugging-with-ipython
# import ipdb; ipdb.set_trace()

import requests
import json
import re

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
DILIDILI_DOMAIN_NAME = 'www.dilidili.com'
DILIDILI_BASE_URL = "http://{0}/".format(DILIDILI_DOMAIN_NAME)
DILIDILI_VEDIO_URL_FORMAT = DILIDILI_BASE_URL + "watch/{0}/"

def extract_iframe_url(vid):
    headers = {'User-Agent': USER_AGENT, 'Referer': DILIDILI_BASE_URL, 'Host': DILIDILI_DOMAIN_NAME}
    r = requests.get(DILIDILI_VEDIO_URL_FORMAT.format(vid), headers = headers)
    regex = re.compile('<iframe.*src=\\"([^\\"]+)\\"[^>]*></iframe>')
    #regex = re.compile('<iframe(.*)></iframe>')
    print(r.text)
    regex_match = regex.match(r.text)
    print(regex_match.group(1))
    print(regex_match.group(2))

if __name__ == '__main__':
    extract_iframe_url(26780)