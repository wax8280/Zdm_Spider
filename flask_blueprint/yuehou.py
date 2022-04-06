import time
import datetime

from flask import request, abort, render_template, Blueprint
from peewee import JOIN, fn
from concurrent.futures import ThreadPoolExecutor

from Cleaner.zdm_cleaner import ZdmCleaner
from Spider.fund_spider import FundSpider
from Spider.zdm_spider import ZdmSpider
from config import sdm_page
from db.orm import Article, ReadRec, db, FocusItem
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


def wrap_item(article_query):
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

    return result, article_ids_str


def insert_read(read_ids, user_name):
    read_to_insert = []
    for read_id in read_ids:
        read_to_insert.append({
            'username': user_name,
            'article_id': read_id
        })

    if read_to_insert:
        ReadRec.insert_many(read_to_insert).execute()


last_day = {
    'vincent': 0
}


@yuehou.route('/get_article', methods=['GET'])
@auth.login_required
def get_article():
    start_t = time.time()
    user_name = auth.username()
    read_ids = request.args.get('readed').split('^') if request.args.get('readed') else []

    with db.connection_context():
        insert_read(read_ids, user_name)

        # 获取24小时以内的
        t2 = ReadRec.select(ReadRec.username, ReadRec.article_id).where(ReadRec.username == user_name).alias('t2')
        article_query = Article.select().join(t2, JOIN.LEFT_OUTER, on=(Article.article_id == t2.c.article_id)).where(
            (Article.timesort > int(time.time()) - 60 * 60 * 24) & (t2.c.article_id).is_null(True)).order_by(
            Article.article_score.desc()).limit(25)

        update_time = timestamp_to_str(Article.select(fn.MAX(Article.timesort)).scalar())

        result, article_ids_str = wrap_item(article_query)

    if last_day[user_name] != datetime.date.today().day:
        fundspider = FundSpider()
        guozhai_grade, bafeite_grade, danjuan_grade = fundspider.main()
        fund = {
            'guozhai_grade': guozhai_grade,
            'bafeite_grade': bafeite_grade,
            'danjuan_grade': danjuan_grade,
        }

        last_day[user_name] = datetime.date.today().day

        return render_template('yuehou.html',
                               articles=result,
                               article_ids_str=article_ids_str,
                               update_time=update_time[5:-3],
                               handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms',
                               fund=fund,)

    return render_template('yuehou.html',
                           articles=result,
                           article_ids_str=article_ids_str,
                           update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')


@yuehou.route('/get_focus', methods=['GET'])
@auth.login_required
def get_focus():
    start_t = time.time()
    user_name = auth.username()
    read_ids = request.args.get('readed').split('^') if request.args.get('readed') else []

    with db.connection_context():
        insert_read(read_ids, user_name)

        focus_items_query = FocusItem.select(FocusItem.username, FocusItem.key_words, FocusItem.thresh_hold).where(
            FocusItem.username == user_name)

        focus_items = [(item.key_words, item.thresh_hold) for item in focus_items_query]

        all_result = []
        all_article_ids_str = ''

        t2 = ReadRec.select(ReadRec.username, ReadRec.article_id).where(ReadRec.username == user_name).alias('t2')

        for each_focus_item in focus_items:
            key_words, thresh_hold = each_focus_item

            if '买到就是赚' in key_words or '免费领' in key_words or '历史低价' in key_words or '国民爆款' in key_words \
                    or '复古款' in key_words or '平替款' in key_words or '必看促销' in key_words or '必领神券' in key_words \
                    or '悦己主义' in key_words or '情怀党' in key_words or '手慢无' in key_words or '新品尝鲜' in key_words \
                    or '新国货' in key_words or '智能家' in key_words or '权威背书' in key_words or '治愈系' in key_words \
                    or '环保生活' in key_words or '白菜党' in key_words or '硬核' in key_words or '简约设计' in key_words \
                    or '经典款' in key_words or '绝对值' in key_words or '老字号' in key_words or '联名款' in key_words or \
                    '行业标杆' in key_words or '跟着买' in key_words or '限定款' in key_words or '高端秀' in key_words or \
                    '高颜值' in key_words or '黑科技' in key_words:
                article_query = Article.select().join(t2, JOIN.LEFT_OUTER,
                                                      on=(Article.article_id == t2.c.article_id)).where(
                    (Article.timesort > int(time.time()) - 60 * 60 * 24) &
                    (t2.c.article_id).is_null(True) &
                    (Article.article_score > thresh_hold) &
                    (Article.zhifa_tag.contains(key_words))
                ).order_by(Article.article_score.desc())
            else:
                article_query = Article.select().join(t2, JOIN.LEFT_OUTER,
                                                      on=(Article.article_id == t2.c.article_id)).where(
                    (Article.timesort > int(time.time()) - 60 * 60 * 24) &
                    (t2.c.article_id).is_null(True) &
                    (Article.article_score > thresh_hold) &
                    (Article.article_title.contains(key_words))
                ).order_by(Article.article_score.desc())

            result, _ = wrap_item(article_query)
            all_result.extend(result)

        all_result = sorted(all_result, key=lambda i: i['article_score'], reverse=True)[:50]
        article_ids_str = '^'.join([i['article_id'] for i in all_result])

        update_time = timestamp_to_str(Article.select(fn.MAX(Article.timesort)).scalar())

    return render_template('focus.html',
                           articles=all_result,
                           article_ids_str=article_ids_str,
                           update_time=update_time[5:-3],
                           handle_time=str(float(str(time.time() - start_t)[:5]) * 1000) + 'ms')
