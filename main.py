import time

from Cleaner.zdm_cleaner import ZdmCleaner
from Spider.zdm_spider import ZdmSpider
from config import sdm_page, smd_time_interval, smd_time_sleep
from lib.log import Log

if __name__ == '__main__':
    zdm_spider = ZdmSpider()
    zdm_cleaner = ZdmCleaner()
    logger = Log('Main')

    while True:
        for i in range(sdm_page):
            res = zdm_spider.spider(i + 1)
            pic_url = []

            if res:
                pic_url = zdm_cleaner.clean(res)
                logger.logi('写库成功，第{}页'.format(i + 1))
            else:
                logger.logw('无法获得res.')

            for url in pic_url:
                zdm_spider.down_pic(url)
            logger.logi('等待{}秒.'.format(smd_time_sleep))
            time.sleep(smd_time_sleep)

        logger.logi('等待{}秒.'.format(smd_time_interval))
        time.sleep(smd_time_interval)
