from mesa import Agent

class RunwayController(Agent):
    """Agent kontrolujący pas startowy, kolejkę lądowania i startów"""
    
    def __init__(self, model, unique_id, wind_direction="07"):
        super().__init__(model)
        self.unique_id = unique_id
        self.is_busy = False
        self.current_airplane = None
        self.current_operation = None  # "landing" lub "departure"
        self.runway_queue = []  # Kolejka samolotów oczekujących na pasie startowym
        self.wind_direction = wind_direction  # "07" lub "25"
        self.active_runway = None  # Aktywny węzeł pasa startowego
        self.set_active_runway()
    
    def set_active_runway(self):
        """Ustaw aktywny pas startowy na podstawie kierunku wiatru"""
        runway_nodes = self.model.graph.get_runway_nodes()
        if runway_nodes:
            # RWY_07 ma id=1, RWY_25 ma id=2
            if self.wind_direction == "07":
                self.active_runway = 1  # Lądowanie od strony 07
            else:
                self.active_runway = 2  # Lądowanie od strony 25
    
    def get_active_runway(self):
        """Zwraca aktywny węzeł pasa startowego"""
        return self.active_runway

    def get_runway_entry_node(self):
        """Zwraca węzeł wejścia na pas startowy"""
        if self.wind_direction == "07":
            return 2
        else:
            return 1
    
    def step(self):
        """Logika kontrolera pasa startowego"""
        if self.is_busy or not self.active_runway:
            return

        now = self.model.step_count
        # Priorytet dla samolotów na pasie startowym
        if self.runway_queue:
            airplane = self.runway_queue[0]
            print(f"Samolot {airplane.unique_id} w kolejce na pasie startowym")
            print(f"Samolot {airplane.airplane_type}")
            if airplane.airplane_type == "arrival":
                granted,blocked_edges = self.model.segment_manager.request_airport_section("runway", airplane.unique_id)
                if granted:
                    if airplane.choose_exit():
                        airplane.blocked_edges = blocked_edges
                        airplane = self.runway_queue.pop(0)
                        self._start_operation(airplane)
                        return
                else:
                    self.model.segment_manager.release_edges(blocked_edges, airplane.unique_id)
                        
            elif airplane.airplane_type == "departure":
                granted,blocked_edges = self.model.segment_manager.request_airport_section("runway", airplane.unique_id)
                if granted:
                    airplane.blocked_edges = blocked_edges
                    airplane = self.runway_queue.pop(0)
                    self._start_operation(airplane)
                    return
                else:
                    self.model.segment_manager.release_edges(blocked_edges, airplane.unique_id)
                    

    
    def add_to_runway_queue(self, airplane):
        """Dodaj samolot do kolejki na pasie startowym"""
        if airplane not in self.runway_queue:
            self.runway_queue.append(airplane)
    

    def finish_landing(self):
        """Zakończenie lądowania"""
        self.is_busy = False
        self.current_airplane = None
        self.current_operation = None
    
    def finish_departure(self):
        """Zakończenie startu"""
        self.is_busy = False
        self.current_airplane = None
        self.current_operation = None
    
    def get_runway_queue_length(self):
        """Zwraca długość kolejki lądowań"""
        return len(self.runway_queue)
    
    def get_runway_queue_info(self):
        """Zwraca informacje o kolejce lądowań"""
        return [f"A{plane.unique_id}" for plane in self.runway_queue]
    

    # --- Metody pomocnicze ---
    def _start_operation(self, airplane):
        """Przygotuj samolot do operacji na pasie."""
        self.is_busy = True
        self.current_airplane = airplane
        airplane.is_in_queue = False

        if airplane.airplane_type == "arrival":
            self.current_operation = "landing"
    
            airplane.current_node = self.active_runway

            runway_pos = self.model.graph.get_node_position(self.active_runway)
            if runway_pos:
                airplane.position.x, airplane.position.y = runway_pos
                airplane.position.current_node = self.active_runway

            airplane.state = "landing"
            airplane.landing_time = 0
        else:
            self.current_operation = "departure"
            airplane.target_node = self.active_runway
            airplane.path = self.model.graph.find_shortest_path(airplane.current_node, airplane.target_node)
            if len(airplane.path) > 1:
                airplane.path.pop(0)
            airplane.state = "departing"
            airplane.departure_time = 0

    def _can_land_now(self, _now: int) -> bool:
        return True

    def _can_depart_now(self, _now: int) -> bool:
        return True

    def _landing_duration_ticks(self) -> int:
        return 3

    def _takeoff_duration_ticks(self) -> int:
        return 3