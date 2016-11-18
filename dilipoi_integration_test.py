import nose
import logging
import dilipoi

class TestDilipoi():
    # Video invalid
    # def test_prepare_to_play_old_bangumi_1(self):
    #     """
    #     Test an old bangumi, 寒蝉鸣泣之时OVA 第01话 羞晒篇
    #     """
    #     yield self.prepare_to_play_bangumi, '-----Start testing for "寒蝉鸣泣之时OVA 第01话 羞晒篇, http://www.dilidili.com/watch/15508/"-----', 'watch/15508/'

    def test_prepare_to_play_old_bangumi_2(self):
        """
        Test an old bangumi, 棺姬嘉依卡 第一季 第1话 背棺材的少女
        """
        yield self.prepare_to_play_bangumi, '-----Start testing for "棺姬嘉依卡 第一季 第1话 背棺材的少女, http://www.dilidili.com/watch/9147/"-----', 'watch/9147/'

    # Video invalid
    # def test_prepare_to_play_new_bangumi_1(self):
    #     """
    #     Test a new bangumi, 双星之阴阳师 第1话 命中注定的两人
    #     """
    #     yield self.prepare_to_play_bangumi, '-----Start testing for "双星之阴阳师 第1话 命中注定的两人, http://www.dilidili.com/watch3/30756/"-----', 'watch3/30756/'

    # Video invalid
    # def test_prepare_to_play_new_bangumi_2(self):
    #     """
    #     Test a new bangumi, 美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程
    #     """
    #     yield self.prepare_to_play_bangumi, '-----Start testing for "美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程, http://www.dilidili.com/watch3/43701/"-----', 'watch3/43701/'

    def test_prepare_to_play_new_bangumi_3(self):
        """
        Test a new bangumi, 吹响吧！上低音号 第2季 第7话 车站大楼音乐会
        """
        yield self.prepare_to_play_bangumi, '-----Start testing for "吹响吧！上低音号 第2季 第7话 车站大楼音乐会, http://www.dilidili.com/watch3/52913/"-----', 'watch3/52913/'
    
    def test_prepare_to_play_new_bangumi_4(self):
        """
        Test a new bangumi, 无畏魔女 第6话 召唤好运
        """
        yield self.prepare_to_play_bangumi, '-----Start testing for "无畏魔女 第6话 召唤好运, http://www.dilidili.com/watch3/52915/"-----', 'watch3/52915/'
    
    def test_prepare_to_play_new_bangumi_5(self):
        """
        Test a new bangumi, 魔法少女奈叶 ViVid Strike! 第7话 高町薇薇欧
        """
        yield self.prepare_to_play_bangumi, '-----Start testing for "魔法少女奈叶 ViVid Strike! 第7话 高町薇薇欧, http://www.dilidili.com/watch3/52620/"-----', 'watch3/52620/'

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

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    nose.main()
