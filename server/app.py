#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            new_user = User(
                        username = request.json['username'],
                        image_url = request.json['image_url'],
                        bio = request.json['bio']
                        )
            
            new_user.password_hash = request.json['password']
            
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            new_user_dict = new_user.to_dict()
            response = make_response(jsonify(new_user_dict), 201)
            return response
        except Exception as exc:
            response = make_response(f'{exc}', 422)
            return response

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == session['user_id']).first()
            response = make_response(jsonify(user.to_dict()), 200)
            return response
        
        response_body = {
            'message': 'Not logged in'
        }
        response = make_response(jsonify(response_body), 401)
        return response
    

class Login(Resource):
    def post(self):
        user = User.query.filter(User.username == request.json['username']).first()
        password = request.json['password']
        if user and user.authenticate(password):
            session['user_id'] = user.id
            response = make_response(jsonify(user.to_dict()), 200)
            return response
        
        response = make_response(jsonify({'errors': ['401 Unauthorized']}), 401)
        return response

class Logout(Resource):
    def delete(self):
        if 'user_id' in session and session['user_id']:
            session['user_id'] = None
            response = make_response({}, 204)
            return response
        
        response = make_response({'error': '401 Unauthorized'}, 401)
        return response    





class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter_by(id=session['user_id']).first()
            recipes = [recipe.to_dict() for recipe in user.recipes]
            return recipes, 200
        return {'errors': '401 Unauthorized'}, 401
    
    def post(self):
        try:
            if session['user_id']:
                new_recipe = Recipe(
                                title = request.json['title'],
                                instructions = request.json['instructions'],
                                minutes_to_complete = request.json['minutes_to_complete'],
                                user_id = session['user_id']
                            )
                
                db.session.add(new_recipe)
                db.session.commit()

                return new_recipe.to_dict(rules=('-user.recipes',)), 201
            
            return {'errors': '401 Unauthorized'}, 401

        except Exception as exc:
            return {'errors': f'{exc}'}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)