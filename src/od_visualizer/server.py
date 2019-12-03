# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
from flask import render_template
import json
from server_functions import bike_flows, load_districts, load_subway, load_data17, load_cptm, load_graph, load_curitiba, load_zonas, load_graph_zonas, list_distritos, list_zonas
from sp_grid import create
import json

app = Flask(__name__, static_url_path='', 
            static_folder='static')
api = Api(app)

metro = load_subway()

cptm = load_cptm()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bike")
def bike():
    return render_template("bike.html")
  
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
        horarioInicio = args['horarioInicio']
        horarioFim = args['horarioFim']
        motivo = args['motivo']
        origin = args['origin']
        flow = "NOME_O"
        if origin != "0":
            flow = "NOME_D"

        mapa = load_districts(vehicle_type, sexo, horarioInicio, horarioFim, origin, flow, motivo, True)
        return mapa

class Zonas(Resource):
    def get(self):
        args = request.args
        vehicle_type = args['vehicleType']
        sexo = args['sexo']
        horarioInicio = args['horarioInicio']
        horarioFim = args['horarioFim']
        motivo = args['motivo']
        origin = args['origin']
        flow = "ZONA_O"
        if origin != "0":
            flow = "ZONA_D"
        mapa = load_zonas(vehicle_type, sexo, horarioInicio, horarioFim, origin, flow, motivo, True)
        return mapa

class Pontos(Resource):
    def get(self):
        data17 = load_data17()
        return data17['coords'].to_json()


class Graph(Resource):
    def get(self):
        args = request.args
        vehicle_type = args['vehicleType']
        sexo = args['sexo']
        horarioInicio = args['horarioInicio']
        horarioFim = args['horarioFim']
        origin = args['origin']
        motivo = args['motivo']
        mapa = load_graph(vehicle_type, sexo, horarioInicio, horarioFim, origin, 'NOME_D', motivo)
        return mapa

class GraphZonas(Resource):
    def get(self):
        args = request.args
        vehicle_type = args['vehicleType']
        sexo = args['sexo']
        horarioInicio = args['horarioInicio']
        horarioFim = args['horarioFim']
        origin = args['origin']
        motivo = args['motivo']
        mapa = load_graph_zonas(vehicle_type, sexo, horarioInicio, horarioFim, origin, 'ZONA_D', motivo)
        return mapa

class Curitiba(Resource):
    def get(self):
        return load_curitiba().to_json()  



class Fluxos(Resource):
    def get(self):
        args = request.args
        elevacao = args['elevacao']
        distanciaMenor = args['distanciaMenor']
        distanciaMaior = args['distanciaMaior']
        tempo = args['tempo']
        flow = args['flow']
        fluxos = bike_flows(elevacao, distanciaMenor, distanciaMaior, tempo, flow)
        return fluxos.to_json()      

class Grids(Resource):
    def get(self):
        return create().geodataframe().to_json()      


class ListZonas(Resource):
    def get(self):
        return list_zonas()


class ListDistritos(Resource):
    def get(self):
        return list_distritos()

api.add_resource(Metro, '/metro')
api.add_resource(Distritos, '/distritos') 
api.add_resource(Pontos, '/pontos')
api.add_resource(CPTM, '/cptm')
api.add_resource(Graph, '/grafo')
api.add_resource(GraphZonas, '/grafo_zonas')
api.add_resource(Curitiba, '/curitiba')
api.add_resource(Zonas, '/zonas')
api.add_resource(Fluxos, '/fluxos')
api.add_resource(Grids, '/grids')
api.add_resource(ListZonas, '/list_zonas')
api.add_resource(ListDistritos, '/list_distritos')

if __name__ == '__main__':
     app.run(host='0.0.0.0', port='30116')