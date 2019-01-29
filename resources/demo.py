from flask_restful import Resource
from Model import User

class Demo(Resource):
    def get(self):
        user = User.query.all()[0].username
        return {"message": user}

    def post(self):
        return {"message": "Hello, World!"}