from src.graph import AirportGraph
from src.agents.airplane import Airplane
from src.agents.runway_controler import RunwayController
from src.segment_manager import SegmentManager
from mesa import Model
import os

class AirportModel(Model):
    def __init__(self, num_arriving_airplanes=5, wind_direction="07", 
                 arrival_rate=0.1, nodes_file="nodes.csv", edges_file="edges.csv"):
        super().__init__()
        
        # Inicjalizacja grafu lotniska
        self.graph = AirportGraph(nodes_file, edges_file)
        
        # Pobieranie granic grafu dla wizualizacji
        min_x, max_x, min_y, max_y = self.graph.get_graph_bounds()
        self.width = max_x - min_x + 100  # dodajemy margines
        self.height = max_y - min_y + 100
        
        self.num_arriving_airplanes = num_arriving_airplanes
        self.arrival_rate = arrival_rate  # Prawdopodobieństwo pojawienia się nowego samolotu
        self.wind_direction = wind_direction  # Kierunek wiatru "07" lub "25"
        
        # Runway controller z kierunkiem wiatru
        self.runway_controller = RunwayController(self, 1, wind_direction=wind_direction)
        
        # Segment manager do zarządzania rezerwacjami
        self.segment_manager = SegmentManager(self)  # Przekaż referencję do modelu

        # Lista samolotów w symulacji
        self.airplanes = []
        self.next_airplane_id = 2  # Zaczynamy od 2 (1 jest dla kontrolera)
        
        # Tworzenie początkowych samolotów przybywających
        self.create_initial_arrivals()

        self.running = True
        self.step_count = 0

    def create_initial_arrivals(self):
        """Tworzy początkowe samoloty przybywające do lądowania"""
        for i in range(self.num_arriving_airplanes):
            airplane = Airplane(self, self.next_airplane_id, airplane_type="arrival")
            # Samoloty przybywające nie mają jeszcze pozycji (są w powietrzu)
            airplane.current_node = None
            # Ustaw priorytet samolotu w segment managerze
            self.segment_manager.set_airplane_priority(self.next_airplane_id, airplane.priority)
            self.airplanes.append(airplane)
            self.next_airplane_id += 1
    
    def spawn_new_arrival(self):
        """Spawuje nowy samolot przybywający"""
        if self.random.random() < self.arrival_rate:
            airplane = Airplane(self, self.next_airplane_id, airplane_type="arrival")
            airplane.current_node = None
            # Ustaw priorytet samolotu w segment managerze
            self.segment_manager.set_airplane_priority(self.next_airplane_id, airplane.priority)
            self.airplanes.append(airplane)
            self.next_airplane_id += 1

    def step(self):
        """Krok symulacji"""
        self.step_count += 1
        
        # Czasami spawuj nowe samoloty
        self.spawn_new_arrival()
        
        # Wyczyść stare rezerwacje
        self.segment_manager.cleanup_old_reservations(self.step_count)
        
        # Krok dla wszystkich agentów
        # Najpierw runway controller
        self.runway_controller.step()
        
        # Przetwórz propozycje konfliktów dla wszystkich samolotów
        for airplane in self.airplanes:
            airplane.process_conflict_proposals()
        
        # Potem wszystkie samoloty (kopiujemy listę, bo może się zmienić)
        for airplane in self.airplanes[:]:
            airplane.step()


    def portray_cell(cell_type):
        colors = {
            "R": "#7f7f7f",  # runway (ciemnoszary)
            "T": "#bfbfbf",  # taxiway
            "A": "#9999ff",  # apron
            "M": "#66cc66",  # terminal
            "G": "#aaffaa",  # grass
        }
        return {"Shape": "rect", "Color": colors[cell_type], "Filled": True, "Layer": 0}