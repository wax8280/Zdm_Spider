from flask_httpauth import HTTPBasicAuth

from config import Username

auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    for user in Username:
        if user['username'] == username:
            return user['password']
    return None
