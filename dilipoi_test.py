import nose
import logging
import dilipoi

class TestDilipoi():
    def test_prepare_to_play_old_bangumi(self):
        """
        Test an old bangumi, 寒蝉鸣泣之时OVA 第01话 羞晒篇
        """
        #logging.info('-----Start testing for "寒蝉鸣泣之时OVA 第01话 羞晒篇, http://www.dilidili.com/watch/15508/"-----')
        yield self.prepare_to_play_bangumi, '-----Start testing for "寒蝉鸣泣之时OVA 第01话 羞晒篇, http://www.dilidili.com/watch/15508/"-----', 'watch/15508/'

    def test_prepare_to_play_new_bangumi_1(self):
        """
        Test a new bangumi, 双星之阴阳师 第1话 命中注定的两人
        """
        #logging.info('-----Start testing for "双星之阴阳师 第1话 命中注定的两人, http://www.dilidili.com/watch3/30756/"-----')
        yield self.prepare_to_play_bangumi, '-----Start testing for "双星之阴阳师 第1话 命中注定的两人, http://www.dilidili.com/watch3/30756/"-----', 'watch3/30756/'

    def test_prepare_to_play_new_bangumi_2(self):
        """
        Test a new bangumi, 美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程
        """
        #logging.info('-----Start testing for "美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程, http://www.dilidili.com/watch3/43701/"-----')
        yield self.prepare_to_play_bangumi, '-----Start testing for "美少女战士crystal 死亡毁灭者篇 第13话 无限大 启程, http://www.dilidili.com/watch3/43701/"-----', 'watch3/43701/'

    def prepare_to_play_bangumi(self, test_case_title, dili_video_url):
        logging.info(test_case_title)
        video_type, video_title, video_urls = dilipoi.DiliPoi(dili_video_url).prepare_to_play()
        logging.info("Video type: '{0}'".format(video_type))
        logging.info("Video title: '{0}'".format(video_title))
        logging.info("Video urls: '{0}'".format(video_urls))
        nose.tools.assert_is_not_none(video_type)
        nose.tools.assert_is_not_none(video_title)
        nose.tools.assert_is_not_none(video_urls)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    nose.main()
