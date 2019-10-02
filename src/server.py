# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
import json
from server_functions import load_districts, load_subway, load_data17

app = Flask(__name__)
api = Api(app)

mapa = load_districts()

metro = load_subway()

data17 = load_data17()

class Metro(Resource):
    def get(self):
        return metro.to_json()


class Distritos(Resource):
    def get(self):
        return mapa.to_json()

class Pontos(Resource):
    def get(self):
        return data17['coords'].to_json()

api.add_resource(Metro, '/metro')
api.add_resource(Distritos, '/distritos') 
api.add_resource(Pontos, '/pontos')


if __name__ == '__main__':
     app.run(port='5002')