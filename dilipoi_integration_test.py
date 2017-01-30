import nose
import logging
import requests
import dilipoi
#import ipdb

class TestDilipoi():
    def test_prepare_to_play_old_bangumi_1(self):
        """
        Test an old bangumi, 寒蝉鸣泣之时OVA 第01话 羞晒篇
        """
        video_path = 'watch/15508'
        video_brief = '寒蝉鸣泣之时OVA 第01话 羞晒篇, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
        yield self.prepare_to_play_bangumi, '-----Start testing for {0}-----'.format(video_brief), video_path

    # Video invali
    # def test_prepare_to_play_old_bangumi_2(self):
    #     """
    #     Test an old bangumi, 棺姬嘉依卡 第一季 第1话 背棺材的少女
    #     """
    #     video_path = 'watch/9147'
    #     video_brief = '棺姬嘉依卡 第一季 第1话 背棺材的少女, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
    #     yield self.prepare_to_play_bangumi, '-----Start testing for {0}'.format(video_brief), video_path

    # Video invalid
    # def test_prepare_to_play_new_bangumi_1(self):
    #     """
    #     Test a new bangumi, 双星之阴阳师 第1话 命中注定的两人
    #     """
    #     video_path = 'watch/9147'
    #     video_brief = '双星之阴阳师 第1话 命中注定的两人, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
    #     yield self.prepare_to_play_bangumi, '-----Start testing for {0}-----'.format(video_brief), video_path

    # Video invalid
    # def test_prepare_to_play_new_bangumi_2(self):
    #     """
    #     Test a new bangumi, 美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程
    #     """
    #     video_path = 'watch/43701'
    #     video_brief = '美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
    #     yield self.prepare_to_play_bangumi, '-----Start testing for {0}-----'.format(video_brief), video_path

    # Video invalid
    # def test_prepare_to_play_new_bangumi_3(self):
    #     """
    #     Test a new bangumi, 吹响吧！上低音号 第2季 第7话 车站大楼音乐会
    #     """
    #     video_path = 'watch/52913'
    #     video_brief = '吹响吧！上低音号 第2季 第7话 车站大楼音乐会, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
    #     yield self.prepare_to_play_bangumi, '-----Start testing for {0}-----'.format(video_brief), video_path
    
    # Video invalid
    # def test_prepare_to_play_new_bangumi_4(self):
    #     """
    #     Test a new bangumi, 无畏魔女 第6话 召唤好运
    #     """
    #     video_path = 'watch/52915'
    #     video_brief = '无畏魔女 第6话 召唤好运, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
    #     yield self.prepare_to_play_bangumi, '-----Start testing for {0}-----'.format(video_brief), video_path
    
    # Video invalid
    # def test_prepare_to_play_new_bangumi_5(self):
    #     """
    #     Test a new bangumi, 魔法少女奈叶 ViVid Strike! 第7话 高町薇薇欧
    #     """
    #     video_path = 'watch/52620'
    #     video_brief = '魔法少女奈叶 ViVid Strike! 第7话 高町薇薇欧, {0}/{1}'.format(dilipoi.DILIDILI_BASE_URL, video_path)
    #     yield self.prepare_to_play_bangumi, '-----Start testing for {0}-----'.format(video_brief), video_path

    def prepare_to_play_bangumi(self, test_case_title, dili_video_url):
        logging.info(test_case_title)
        video_type, video_title, video_urls = dilipoi.DiliPoi(dili_video_url).prepare_to_play()
        logging.info("Video type: '{0}'".format(video_type))
        logging.info("Video title: '{0}'".format(video_title))
        logging.info("Video urls: '{0}'".format(video_urls))
        nose.tools.assert_is_not_none(video_type)
        nose.tools.assert_is_not_none(video_title)
        nose.tools.assert_is_not_none(video_urls)
        if video_type == dilipoi.VideoType.yun:
            nose.tools.assert_is_instance(video_urls, str)
        else:
            nose.tools.assert_is_instance(video_urls, list)
            for video_url in video_urls:
                self.check_video_url_content_type(video_url)

    def check_video_url_content_type(self, video_url):
        logging.info("Check content type of video url: '{0}'".format(video_url))
        #ipdb.set_trace()
        response = requests.head(video_url, headers=None, allow_redirects=True)
        nose.tools.ok_(response.headers['content-type'].startswith('video/'))


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    nose.main()
