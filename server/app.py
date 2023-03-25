#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


# log in
class Login(Resource):
    def post(self):
        # gets a username from request's JSON.
        user = User.query.filter(User.username==request.get_json()["username"]).first()

        # set value of the session's user_id value to the user's id.
        session["user_id"] = user.id
        # returns the user as JSON with a 200 status code.
        return make_response(jsonify(user.to_dict()), 200)

# stay logging in, even after refreshing the page.
class CheckSession(Resource):
    def get(self):
        # retrieves the user_id value from the session.
        user = User.query.filter(User.id==session.get("user_id")).first()

        if not user:
            # if the session does not have a user_id, get() returns no data and a 401 (Unauthorized) status code.
            return make_response(jsonify({}), 401)
        # If the session has a user_id, get() returns the user as JSON with a 200 status code.
        return make_response(jsonify(user.to_dict()), 200)

api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')


# logout
class Logout(Resource):
    # has one route, delete()
    def delete(self):
        # delete() removes the user_id value from the session.
        # set user_id to None when logout
        session['user_id'] = None

        # returns no data and a 204 (No Content) status code.
        return make_response(jsonify({'message': "204: No content"}), 204)
api.add_resource(Logout, "/logout")




if __name__ == '__main__':
    app.run(port=5555, debug=True)
