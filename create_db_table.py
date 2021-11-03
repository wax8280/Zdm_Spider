from db.orm import User, ReadRec, Article

if __name__ == "__main__":
    User.create_table()
    ReadRec.create_table()
    Article.create_table()