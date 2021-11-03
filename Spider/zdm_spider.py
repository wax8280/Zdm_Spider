import re
import time
import traceback

import requests

from config import cookies
from lib import md5string
from lib.log import Log

requests.packages.urllib3.disable_warnings()


class ZdmSpider:
    """用于数据的爬取及清洗"""

    def __init__(self, retry_count=5, retry_time_sleep=5):
        self.session = requests.session()
        self.logger = Log('Spider')
        self.retry_count = retry_count
        self.retry_time_sleep = retry_time_sleep

        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/7\
            0.0.3538.110 Safari/537.36',
            'Referer': 'https://faxian.smzdm.com/h2s0t0f0c0p1/',
            'Cookie': cookies
        }

    def down_pic(self, url):
        if not url:
            return

        retry_time = 0
        try:

            while retry_time < self.retry_count:
                try:
                    res = requests.get(url, headers=self.headers, verify=False)
                    pic_name = md5string(url)
                    try:
                        p = re.findall('\.(\w*)?$', url)[0]
                    except:
                        p = 'jpg'
                    with open('./static/pic/{}.{}'.format(pic_name, p), 'wb') as f:
                        f.write(res.content)
                    self.logger.logi('写入图片{}成功!'.format(pic_name))
                    return
                except:
                    self.logger.logw('爬虫失败，错误信息{}'.format(traceback.format_exc()))
                    retry_time += 1
        except:
            pass

    def spider(self, page):
        retry_time = 0
        try:

            while retry_time < self.retry_count:
                try:
                    res = requests.get('https://faxian.smzdm.com/json_more?filter=h2s0t0f0c0&page={}'.format(page),
                                       headers=self.headers, verify=False)
                    self.logger.logi('开始请求{}'.format(page))
                    return res
                except:
                    self.logger.logw('爬虫失败，错误信息{}'.format(traceback.format_exc()))
                    retry_time += 1
                    time.sleep(self.retry_time_sleep)
        except:
            self.logger.loge('无法获取信息，错误信息:{}'.format(traceback.format_exc()))
            return ''
