import re
import time

from db.orm import Article
from lib import md5string


class ZdmCleaner:
    def __init__(self):
        pass

    def clean(self, res):
        res_json = res.json()
        if type(res_json) == list:
            res_list = res_json
        else:
            res_list = []
            for k, v in res_json.items():
                res_list.append(v)

        pic_url = []

        for item in res_list:
            # '1.5k'这种需要特殊处理
            if 'k' not in str(item.get('article_collection', '')):
                article_collection = int(item.get('article_collection', ''))
            else:
                article_collection = int(float(item.get('article_collection', '').replace('k', '')) * 1000)

            if 'k' not in str(item.get('article_comment', '')):
                article_comment = int(item.get('article_comment', ''))
            else:
                article_comment = int(float(item.get('article_comment', '').replace('k', '')) * 1000)

            if 'k' not in str(item.get('article_rating', '')):
                article_rating = int(item.get('article_rating', ''))
            else:
                article_rating = int(float(item.get('article_rating', '').replace('k', '')) * 1000)

            # 计算分数
            time_diff = int(time.time()) - int(item.get('timesort', ''))

            # 惩罚系数，针对赞、收藏比评论多很多的情况
            if article_comment == 0 and (article_collection > 10 or article_rating > 10):
                # 如果评论是0的话，收藏或值有任意一个超过10的话，惩罚系数为0.3
                penalty_factor = 0.3
            elif max((article_collection, article_rating)) == 0 and article_comment != 0:
                # 对于收藏、赞为0的，惩罚系数为0.8
                penalty_factor = 0.8
            elif max((article_collection, article_rating)) == 0 and article_comment == 0:
                penalty_factor = 0.5
            else:
                # 如10条评论，40条收藏，30个赞。则惩罚系数为10/40+0.5=0.9，如果大于1，则取1
                penalty_factor = min((article_comment / max([article_collection, article_rating]) + 0.5, 1))

            article_score = int(
                (article_comment * 0.5 + article_rating * 0.2 + article_collection * 0.3) * penalty_factor / time_diff * 100000
            )

            zhifa_tag = item['zhifa_tag'].get('name') if item['zhifa_tag'] else ''

            # 处理html标签
            article_content = re.sub('<.*?$', '', re.sub('<.*?>', '', item.get('article_content', '')))

            if Article.select().where(Article.article_id == item['article_id']).exists():
                Article.update(
                    article_content=article_content,
                    timesort=str(item.get('timesort', '')),
                    article_link=item.get('article_link', ''),
                    article_url=item.get('article_url', ''),
                    article_mall=item.get('article_mall', ''),
                    article_pic_url=item.get('article_pic_url', ''),
                    article_price=item.get('article_price', ''),
                    article_rating=article_rating,
                    article_title=item.get('article_title', ''),
                    article_top_category=item.get('article_top_category', ''),
                    price_level=item['gtm'].get('dimension4', ''),
                    article_collection=article_collection,
                    article_comment=article_comment,
                    zhifa_tag=zhifa_tag,
                    article_score=article_score,
                    stock_status_note=item.get('stock_status_note', ''),
                ).where(Article.article_id == item['article_id']).execute()
            else:
                try:
                    p = re.findall('\.(\w*)?$', item.get('article_url', ''))[0]
                except:
                    p = 'jpg'
                article = Article.create(
                    article_content=article_content,
                    timesort=str(item.get('timesort', '')),
                    article_link=item.get('article_link', ''),
                    article_url=item.get('article_url', ''),
                    article_mall=item.get('article_mall', ''),
                    article_pic_url=item.get('article_pic_url', ''),
                    article_price=item.get('article_price', ''),
                    article_rating=article_rating,
                    article_title=item.get('article_title', ''),
                    article_top_category=item.get('article_top_category', ''),
                    price_level=item['gtm'].get('dimension4', ''),
                    article_collection=article_collection,
                    article_comment=article_comment,
                    zhifa_tag=zhifa_tag,
                    article_score=article_score,
                    article_id=item['article_id'],
                    local_article_pic_url='{}.{}'.format(md5string(item.get('article_pic_url', '')), p),
                    stock_status_note=item.get('stock_status_note', ''),
                )
                pic_url.append(item.get('article_pic_url', ''))

                article.save()
        return pic_url
