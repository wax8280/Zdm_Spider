import time

from flask import request, abort, render_template, Blueprint
from peewee import JOIN, fn

from db.orm import Article, ReadRec, db
from lib import timestamp_to_str

yuehou = Blueprint('yuehou', __name__, template_folder='templates')

from flask_blueprint import auth


# @app.before_request
# def _db_conn():
#     db.connect()
#
# @app.teardown_request
# def __db_close(exc):
#     if not db.is_closed():
#         db.close()


@yuehou.route('/get_article', methods=['GET'])
@auth.login_required
def get_article():
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
            Article.article_score.desc()).limit(50)

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

    return render_template('base.html', articles=result, article_ids_str=article_ids_str, update_time=update_time)
