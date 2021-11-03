import json
import time

from flask import request, abort, render_template, Blueprint, make_response, redirect

from db.orm import Article, User, ReadRec
from lib import md5string, timestamp_to_str

yuehou = Blueprint('yuehou', __name__, template_folder='templates')

from flask_blueprint import auth


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

    if readed_to_insert:
        ReadRec.insert_many(readed_to_insert).execute()

    # 获取24小时以内的
    article_query = Article.select().where(Article.timesort > int(time.time()) - 60 * 60 * 48).order_by(Article.article_score.desc())
    readed_query = ReadRec.select().where(ReadRec.username == user_name)
    readed_set = set()
    for item in readed_query:
        readed_set.add(item.article_id)

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
            'time_str':timestamp_to_str(item.timesort,format_str="%m-%d %H:%M")
        }

        if a['article_id'] in readed_set:
            continue
        else:
            result.append(a)
            article_ids.append(a['article_id'])

    article_ids_str = '^'.join(article_ids[:30])

    return render_template('base.html', articles=result[:30], article_ids_str=article_ids_str)
