import random
import math
from mesa import Agent


class Airplane(Agent):
    """Agent reprezentujący samolot"""
    
    def __init__(self, model, unique_id):
        super().__init__(model)
        self.unique_id = unique_id
        self.state = "flying"  # flying, approaching, landing, landed
        self.target_x = None
        self.target_y = None
        self.landing_time = 0
        self.max_landing_time = 5  # Kroki potrzebne do wylądowania
        
    def step(self):
        """Główna logika samolotu"""
        if self.state == "flying":
            self.move_towards_runway()
        elif self.state == "approaching":
            self.approach_runway()
        elif self.state == "landing":
            self.land()
    
    def move_towards_runway(self):
        """Ruch w kierunku pasa startowego"""
        current_x, current_y = self.pos
        
        # Jeśli nie ma celu, znajdź najbliższy punkt pasa startowego
        if self.target_x is None:
            runway_y = self.model.height // 2
            self.target_x = random.randint(0, self.model.width - 1)
            self.target_y = runway_y
        
        # Oblicz kierunek ruchu
        dx = self.target_x - current_x
        dy = self.target_y - current_y
        
        # Normalizuj kierunek (ruch o 1 krok)
        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1
        
        new_x = current_x + dx
        new_y = current_y + dy
        
        # Sprawdź czy nowa pozycja jest w granicach
        if 0 <= new_x < self.model.width and 0 <= new_y < self.model.height:
            self.pos = (new_x, new_y)
        
        # Sprawdź czy jest blisko pasa startowego
        if abs(current_y - self.target_y) <= 1:
            self.state = "approaching"
    
    def approach_runway(self):
        """Zbliżanie się do pasa startowego"""
        current_x, current_y = self.pos
        
        # Sprawdź czy pas startowy jest wolny
        if not self.model.runway_controller.is_busy:
            # Poproś o pozwolenie na lądowanie
            if self.model.runway_controller.request_landing(self):
                self.state = "landing"
                self.landing_time = 0
        else:
            # Krążenie w pobliżu pasa startowego
            self.circle_near_runway()
    
    def circle_near_runway(self):
        """Krążenie w pobliżu pasa startowego"""
        current_x, current_y = self.pos
        runway_y = self.model.height // 2
        
        # Ruch w kółko wokół pasa startowego
        if current_y < runway_y - 1:
            new_y = current_y + 1
        elif current_y > runway_y + 1:
            new_y = current_y - 1
        else:
            # Ruch poziomy
            if current_x < self.model.width // 2:
                new_x = current_x + 1
                new_y = current_y
            else:
                new_x = current_x - 1
                new_y = current_y
        
        if 'new_x' in locals():
            if 0 <= new_x < self.model.width and 0 <= new_y < self.model.height:
                self.pos = (new_x, new_y)
        else:
            if 0 <= current_x < self.model.width and 0 <= new_y < self.model.height:
                self.pos = (current_x, new_y)
    
    def land(self):
        """Proces lądowania"""
        self.landing_time += 1
        
        if self.landing_time >= self.max_landing_time:
            self.state = "landed"
            self.model.runway_controller.finish_landing()
    
    def get_color(self):
        """Zwraca kolor dla wizualizacji"""
        if self.state == "flying":
            return "blue"
        elif self.state == "approaching":
            return "orange"
        elif self.state == "landing":
            return "red"
        else:  # landed
            return "green"


class RunwayController(Agent):
    """Agent kontrolujący pas startowy"""
    
    def __init__(self, model, unique_id):
        super().__init__(model)
        self.unique_id = unique_id
        self.is_busy = False
        self.current_airplane = None
        self.queue = []
    
    def step(self):
        """Logika kontrolera pasa startowego"""
        # Jeśli pas jest wolny i są samoloty w kolejce
        if not self.is_busy and self.queue:
            airplane = self.queue.pop(0)
            self.is_busy = True
            self.current_airplane = airplane
    
    def request_landing(self, airplane):
        """Samolot prosi o pozwolenie na lądowanie"""
        if not self.is_busy:
            self.is_busy = True
            self.current_airplane = airplane
            return True
        else:
            if airplane not in self.queue:
                self.queue.append(airplane)
            return False
    
    def finish_landing(self):
        """Zakończenie lądowania"""
        self.is_busy = False
        self.current_airplane = None