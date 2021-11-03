from peewee import *
from config import db_password, db_username, db_host, db_port, db_name

db = MySQLDatabase(db_name, host=db_host, port=db_port, user=db_username, passwd=db_password)
db.connect()


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    login_cookies = CharField()


class Article(BaseModel):
    article_content = CharField()
    article_id = CharField(unique=True, index=True)
    article_link = CharField()
    article_url = CharField()
    article_mall = CharField()
    article_pic_url = CharField()
    article_price = CharField()
    article_rating = IntegerField()
    article_title = CharField()
    article_top_category = CharField()
    price_level = CharField()
    timesort = IntegerField()
    zhifa_tag = CharField()
    article_collection = IntegerField()
    article_comment = IntegerField()
    article_score = FloatField()
    local_article_pic_url = CharField()


class ReadRec(BaseModel):
    username = CharField(index=True)
    article_id = CharField(index=True)


if __name__ == "__main__":
    User.create_table()
    ReadRec.create_table()
    Article.create_table()

    user_name='test'
    # 获取24小时以内的
    article_query = Article.select()
    readed_query = ReadRec.select().where(ReadRec.username == user_name)
    readed_set = set()
    for item in readed_query:
        readed_set.add(item.article_id)

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
            'article_score': item.article_score,
        }

        if a['article_id'] in readed_set:
            continue
        else:
            result.append(a)

    print(result)