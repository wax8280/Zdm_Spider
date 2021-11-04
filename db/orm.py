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
    stock_status_note = CharField()


class ReadRec(BaseModel):
    username = CharField(index=True)
    article_id = CharField(index=True)
