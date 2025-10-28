import random
import math
from mesa import Agent

class RunwayController(Agent):
    """Agent kontrolujący pas startowy, kolejkę lądowania i startów"""
    
    def __init__(self, model, unique_id, wind_direction="07"):
        super().__init__(model)
        self.unique_id = unique_id
        self.is_busy = False
        self.current_airplane = None
        self.current_operation = None  # "landing" lub "departure"
        self.landing_queue = []  # Kolejka samolotów oczekujących na lądowanie
        self.departure_queue = []  # Kolejka samolotów oczekujących na start
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
    
    def step(self):
        """Logika kontrolera pasa startowego"""
        # Jeśli pas jest wolny, obsłuż kolejki (priorytet dla lądowań)
        if not self.is_busy:
            # Najpierw obsługuj lądowania
            if self.landing_queue and self.active_runway:
                airplane = self.landing_queue.pop(0)
                
                # Sprawdź czy można zarezerwować pas startowy
                success, conflict_airplane = self.model.segment_manager.request_segment_with_no_passing(
                    self.active_runway, airplane.unique_id, 1, self.model.step_count
                )
                
                if success:
                    self.is_busy = True
                    self.current_airplane = airplane
                    self.current_operation = "landing"
                    airplane.state = "landing"
                    airplane.landing_time = 0
                    airplane.is_in_queue = False
                    # Umieść samolot na węźle pasa startowego
                    airplane.current_node = self.active_runway
                    # Zainicjalizuj pozycję interpolowaną
                    runway_pos = self.model.graph.get_node_position(self.active_runway)
                    if runway_pos:
                        airplane.position.x, airplane.position.y = runway_pos
                        airplane.position.current_node = self.active_runway
                else:
                    # Pas zajęty - wróć samolot do kolejki
                    self.landing_queue.insert(0, airplane)
                    
            # Jeśli nie ma lądowań, obsługuj starty
            elif self.departure_queue and self.active_runway:
                airplane = self.departure_queue.pop(0)
                
                # Sprawdź czy można zarezerwować pas startowy
                success, conflict_airplane = self.model.segment_manager.request_segment_with_no_passing(
                    self.active_runway, airplane.unique_id, 1, self.model.step_count
                )
                
                if success:
                    self.is_busy = True
                    self.current_airplane = airplane
                    self.current_operation = "departure"
                    airplane.state = "departing"
                    airplane.departure_time = 0
                    airplane.is_in_queue = False
                    # Umieść samolot na węźle pasa startowego
                    airplane.current_node = self.active_runway
                    # Zainicjalizuj pozycję interpolowaną
                    runway_pos = self.model.graph.get_node_position(self.active_runway)
                    if runway_pos:
                        airplane.position.x, airplane.position.y = runway_pos
                        airplane.position.current_node = self.active_runway
                else:
                    # Pas zajęty - wróć samolot do kolejki
                    self.departure_queue.insert(0, airplane)
    
    def add_to_landing_queue(self, airplane):
        """Dodaj samolot do kolejki lądowania"""
        if airplane not in self.landing_queue:
            self.landing_queue.append(airplane)
    
    def add_to_departure_queue(self, airplane):
        """Dodaj samolot do kolejki startów"""
        if airplane not in self.departure_queue:
            self.departure_queue.append(airplane)
    
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
    
    def get_landing_queue_length(self):
        """Zwraca długość kolejki lądowań"""
        return len(self.landing_queue)
    
    def get_departure_queue_length(self):
        """Zwraca długość kolejki startów"""
        return len(self.departure_queue)
    
    def get_landing_queue_info(self):
        """Zwraca informacje o kolejce lądowań"""
        return [f"A{plane.unique_id}" for plane in self.landing_queue]
    
    def get_departure_queue_info(self):
        """Zwraca informacje o kolejce startów"""
        return [f"A{plane.unique_id}" for plane in self.departure_queue]