from db.orm import User, ReadRec, Article,FocusItem

if __name__ == "__main__":
    User.create_table()
    ReadRec.create_table()
    Article.create_table()
    FocusItem.create_table()