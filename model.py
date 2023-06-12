import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flaskuser:okazaki0608@localhost:5432/flask'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)

# デコレータを付与したload_user関数を定義
@login.user_loader
def load_user(id):
    # usersテーブルから指定のidを持つレコードを取り出す
    # flask-loginがこの関数に引数として渡すidの値は文字列であるため、数値に変換する
    return User.query.get(int(id))