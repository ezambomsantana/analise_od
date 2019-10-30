# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
from flask import render_template
import json
from server_functions import bike_flows, load_districts, load_subway, load_data17, load_cptm, load_graph, load_curitiba, load_zonas, load_graph_zonas
from sp_grid import create

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
        origin = args['origin']
        orde = args['orde']
        motivo = args['motivo']
        mapa = load_districts(vehicle_type, sexo, horarioInicio, horarioFim, origin, orde, motivo)
        return mapa.to_json()

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
        orde = args['orde']
        motivo = args['motivo']
        mapa = load_graph(vehicle_type, sexo, horarioInicio, horarioFim, origin, orde, motivo)
        return mapa.to_json()

class GraphZonas(Resource):
    def get(self):
        args = request.args
        vehicle_type = args['vehicleType']
        sexo = args['sexo']
        horarioInicio = args['horarioInicio']
        horarioFim = args['horarioFim']
        origin = args['origin']
        orde = args['orde']
        motivo = args['motivo']
        mapa = load_graph_zonas(vehicle_type, sexo, horarioInicio, horarioFim, origin, 'ZONA_D', motivo)
        return mapa.to_json()

class Curitiba(Resource):
    def get(self):
        return load_curitiba().to_json()  

class Zonas(Resource):
    def get(self):
        args = request.args
        vehicle_type = args['vehicleType']
        sexo = args['sexo']
        horarioInicio = args['horarioInicio']
        horarioFim = args['horarioFim']
        origin = args['origin']
        orde = args['orde']
        motivo = args['motivo']
        mapa = load_zonas(vehicle_type, sexo, horarioInicio, horarioFim, origin, 'ZONA_O', motivo)
        return mapa.to_json()      

class Fluxos(Resource):
    def get(self):
        args = request.args
        elevacao = args['elevacao']
        distancia = args['distancia']
        tempo = args['tempo']
        flow = args['flow']
        fluxos = bike_flows(elevacao, distancia, tempo, flow)
        return fluxos.to_json()      



class Grids(Resource):
    def get(self):
        return create().geodataframe().to_json()      

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

if __name__ == '__main__':
     app.run(port='5002')