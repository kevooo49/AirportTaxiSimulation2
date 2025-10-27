import random
from mesa import Model, Agent
from .agents import Airplane, RunwayController


class AirportModel(Model):
    """Model symulacji lotniska z pasem startowym"""
    
    def __init__(self, width=20, height=10, num_airplanes=5):
        super().__init__()
        self.width = width
        self.height = height
        self.num_airplanes = num_airplanes
        
        # Kontroler pasa startowego
        self.runway_controller = RunwayController(self, 1)
        
        # Tworzenie samolotów
        self.create_airplanes()
        
        self.running = True
        
    def create_airplanes(self):
        """Tworzy samoloty w różnych pozycjach"""
        for i in range(self.num_airplanes):
            # Losowe pozycje startowe (poza pasem startowym)
            while True:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                # Pas startowy to środkowe wiersze
                if not (y >= self.height//2 - 1 and y <= self.height//2 + 1):
                    break
            
            airplane = Airplane(self, i + 2)  # ID zaczyna od 2 (1 to kontroler)
            airplane.pos = (x, y)
    
    def step(self):
        """Krok symulacji"""
        # Aktualizacja wszystkich agentów
        for agent in self.agents:
            agent.step()
        
        # Sprawdź czy wszystkie samoloty wylądowały
        flying_planes = [a for a in self.agents if isinstance(a, Airplane) and a.state == "flying"]
        if not flying_planes and not self.runway_controller.is_busy:
            self.running = False