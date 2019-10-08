# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
import json
from server_functions import load_districts, load_subway, load_data17, load_cptm

app = Flask(__name__)
api = Api(app)

mapa = load_districts("0", "0")

metro = load_subway()

cptm = load_cptm()

data17 = load_data17()

class Metro(Resource):
    def get(self):
        return metro.to_json()

class CPTM(Resource):
    def get(self):
        return cptm.to_json()

class Distritos(Resource):
    def get(self):
        args = request.args
        vehicle_type = args['vehicleType']
        sexo = args['sexo']
        mapa = load_districts(vehicle_type, sexo)
        return mapa.to_json()

class Pontos(Resource):
    def get(self):
        return data17['coords'].to_json()

api.add_resource(Metro, '/metro')
api.add_resource(Distritos, '/distritos') 
api.add_resource(Pontos, '/pontos')
api.add_resource(CPTM, '/cptm')


if __name__ == '__main__':
     app.run(port='5002')