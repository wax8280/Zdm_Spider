import time

from flask import request, abort, render_template, Blueprint
from peewee import JOIN, fn
from concurrent.futures import ThreadPoolExecutor

from Cleaner.zdm_cleaner import ZdmCleaner
from Spider.zdm_spider import ZdmSpider
from config import sdm_page
from db.orm import Article, ReadRec, db
from lib import timestamp_to_str
from lib.log import Log

yuehou = Blueprint('yuehou', __name__, template_folder='templates')
executor = ThreadPoolExecutor(2)

from flask_blueprint import auth


# @app.before_request
# def _db_conn():
#     db.connect()
#
# @app.teardown_request
# def __db_close(exc):
#     if not db.is_closed():
#         db.close()

def start_spider():
    zdm_spider = ZdmSpider()
    zdm_cleaner = ZdmCleaner()
    logger = Log('Flask_Updater')

    with db.connection_context():
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


@yuehou.route('/update_now', methods=['GET'])
@auth.login_required
def update_now():
    executor.submit(start_spider)
    return '正在更新，请稍后...'


def get_hot(hour):
    article_query = Article.select().where(Article.timesort > int(time.time()) - 60 * 60 * hour).order_by(
        Article.article_score.desc()).limit(300)
    update_time = timestamp_to_str(Article.select(fn.MAX(Article.timesort)).scalar())
    result = []

    for item in article_query:
        a = {
            'article_content': item.article_content,
            'article_id': item.article_id,
            'article_link': item.article_link,
            'article_url': item.article_url,
            'article_mall': item.article_mall,
            'article_pic_url': item.article_pic_url,
            'article_price': item.article_price,
            'article_rating': item.article_rating,
            'article_title': item.article_title,
            'article_top_category': item.article_top_category,
            'price_level': item.price_level,
            'timesort': item.timesort,
            'zhifa_tag': item.zhifa_tag,
            'article_collection': item.article_collection,
            'article_comment': item.article_comment,
            'article_score': int(item.article_score),
            'local_article_pic_url': item.local_article_pic_url,
            'stock_status_note': item.stock_status_note,
            'time_str': timestamp_to_str(item.timesort, format_str="%m-%d %H:%M")
        }
        result.append(a)
    return result, update_time


@yuehou.route('/hot3', methods=['GET'])
def hot3():
    start_t = time.time()
    result, update_time = get_hot(3)
    return render_template('hot.html', articles=result, update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')


@yuehou.route('/hot6', methods=['GET'])
def hot6():
    start_t = time.time()
    result, update_time = get_hot(6)
    return render_template('hot.html', articles=result, update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')

@yuehou.route('/hot12', methods=['GET'])
def hot12():
    start_t = time.time()
    result, update_time = get_hot(12)
    return render_template('hot.html', articles=result, update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')

@yuehou.route('/hot24', methods=['GET'])
def hot24():
    start_t = time.time()
    result, update_time = get_hot(24)
    return render_template('hot.html', articles=result, update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')

@yuehou.route('/get_article', methods=['GET'])
@auth.login_required
def get_article():
    start_t = time.time()
    user_name = auth.username()
    readed_ids = request.args.get('readed').split('^') if request.args.get('readed') else []
    readed_to_insert = []

    for readed_id in readed_ids:
        readed_to_insert.append({
            'username': user_name,
            'article_id': readed_id
        })

    with db.connection_context():

        if readed_to_insert:
            ReadRec.insert_many(readed_to_insert).execute()

        # 获取12小时以内的
        t2 = ReadRec.select(ReadRec.username, ReadRec.article_id).where(ReadRec.username == user_name).alias('t2')
        article_query = Article.select().join(t2, JOIN.LEFT_OUTER, on=(Article.article_id == t2.c.article_id)).where(
            (Article.timesort > int(time.time()) - 60 * 60 * 12) & (t2.c.article_id).is_null(True)).order_by(
            Article.article_score.desc()).limit(25)

        update_time = timestamp_to_str(Article.select(fn.MAX(Article.timesort)).scalar())

        result = []
        article_ids = []

        for item in article_query:
            a = {
                'article_content': item.article_content,
                'article_id': item.article_id,
                'article_link': item.article_link,
                'article_url': item.article_url,
                'article_mall': item.article_mall,
                'article_pic_url': item.article_pic_url,
                'article_price': item.article_price,
                'article_rating': item.article_rating,
                'article_title': item.article_title,
                'article_top_category': item.article_top_category,
                'price_level': item.price_level,
                'timesort': item.timesort,
                'zhifa_tag': item.zhifa_tag,
                'article_collection': item.article_collection,
                'article_comment': item.article_comment,
                'article_score': int(item.article_score),
                'local_article_pic_url': item.local_article_pic_url,
                'stock_status_note': item.stock_status_note,
                'time_str': timestamp_to_str(item.timesort, format_str="%m-%d %H:%M")
            }

            result.append(a)
            article_ids.append(a['article_id'])

        article_ids_str = '^'.join(article_ids)

    return render_template('yuehou.html', articles=result, article_ids_str=article_ids_str, update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')
