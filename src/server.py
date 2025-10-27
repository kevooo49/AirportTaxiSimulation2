from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

def run_server():
    model = AirportModel()
    server = ModularServer(AirportModel,
                           [AirportVisualization()],
                           "Airport Runway Simulation",
                           model)
    server.port = 8521  # The default port
    server.launch()