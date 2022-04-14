import json
import re
import traceback

import requests

from lib.log import Log


class FundSpider:
    """用于数据的爬取及清洗"""

    def __init__(self, retry_count=5, retry_time_sleep=5):
        self.session = requests.session()
        self.retry_count = retry_count
        self.retry_time_sleep = retry_time_sleep

        self.guozhai_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.dashiyetouzi.com/tools/compare/hs300_10gz_pro.php',
        }

        self.danjuan_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://danjuanapp.com/djmodule/value-center?channel=1300100141',
        }

        self.bafeite_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',

        }

    def guozhai(self):
        retry_time = 0
        try:

            while retry_time < self.retry_count:
                try:
                    res = requests.post('http://www.dashiyetouzi.com/tools/compare/hs300_10gz_pro_data.php', headers=self.guozhai_headers, verify=False)
                    json_data = res.json()['list'][-1]

                    # ['2022-04-01', 2.94]
                    return json_data
                except:
                    retry_time += 1
        except:
            pass

    def bafeite(self):
        retry_time = 0
        try:

            while retry_time < self.retry_count:
                try:
                    res = requests.get('https://legulegu.com/stockdata/marketcap-gdp', headers=self.bafeite_headers, verify=False)
                    group = re.search('id="data-description">(.*?)年(.*?)月(.*?)日，总市值比GDP值为：(.*?)%</p>', res.text)

                    # ['2022-04-01', 2.94]
                    return ['{}-{}-{}'.format(group.group(1), group.group(2), group.group(3)), group.group(4)]
                except:
                    retry_time += 1
        except:
            pass

    def danjuan(self):
        retry_time = 0
        try:

            result = {}
            while retry_time < self.retry_count:
                try:
                    json_data = requests.get('https://danjuanapp.com/djapi/index_eva/dj', headers=self.danjuan_headers, verify=False).json()

                    for i in json_data['data']['items']:
                        if i['name'] == '沪深300':
                            result['300'] = i['pe']
                        elif i['name'] == '上证50':
                            result['50'] = i['pe']
                except:
                    retry_time += 1
        except:
            pass

        return result

    @staticmethod
    def grade(the_min, the_max, now, grade=10):
        now = float(now)
        s = (the_max - the_min) / (grade - 1)
        s_list = [the_min + s * i for i in range(grade)]

        if now > the_max:
            return grade

        for index, item in enumerate(s_list):
            if item > now:
                return index + 1

    def main(self):
        guozhai_data = self.guozhai()
        bafeite_data = self.bafeite()
        danjuan_data = self.danjuan()

        guozhai_grade = FundSpider.grade(1.6, 3.54, guozhai_data[1], 10)       # 越高风险越小
        bafeite_grade = 11 - FundSpider.grade(20, 120, bafeite_data[1], 10)     # 越高风险越大
        danjuan_hushen_300_grade = 11 - FundSpider.grade(8, 18, danjuan_data['300'], 10)          # 越高风险越大
        danjuan_shangzheng_50_grade = 11 - FundSpider.grade(7, 14.95, danjuan_data['50'], 10)          # 越高风险越大

        return guozhai_grade, bafeite_grade, danjuan_hushen_300_grade,danjuan_shangzheng_50_grade
