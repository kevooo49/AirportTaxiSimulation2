import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from math import isfinite





class AtcController:
    """
    Prosty kontroler ATC dla pasa: zarządza separacjami T/T, L/L, T/L, L/T
    oraz czasem blokady pasa dla line-up / takeoff roll / landing roll + bufor.
    """


    def __init__(self):
        # separacje w sekundach (proste stałe)
        self.sep_TT_s = 60
        self.sep_LL_s = 70
        self.sep_TL_s = 90
        self.sep_LT_s = 90
        # czasy zajęcia pasa
        self.lineup_block_s = 20
        self.takeoff_roll_time_s = 35
        self.landing_roll_time_s = 40
        self.runway_buffer_after_exit_s = 15
        # stan
        self.last_takeoff_time: int = -10**9
        self.last_landing_time: int = -10**9
        self.runway_lock_until: int = 0
        self.last_op: str = ""  # "T" albo "L"

    def can_line_up(self, now: int) -> bool:
        return now >= self.runway_lock_until

    def grant_line_up(self, now: int):
        self.runway_lock_until = max(self.runway_lock_until, now + self.lineup_block_s)
        self.last_op = "T"  # line-up poprzedza start

    def can_takeoff(self, now: int) -> bool:
        # separacja zależna od poprzedniej operacji
        if self.last_op == "T":
            return (now - self.last_takeoff_time) >= self.sep_TT_s and now >= self.runway_lock_until
        if self.last_op == "L":
            return (now - self.last_landing_time) >= self.sep_LT_s and now >= self.runway_lock_until
        return now >= self.runway_lock_until

    def grant_takeoff(self, now: int):
        occ = self.takeoff_roll_time_s + self.runway_buffer_after_exit_s
        self.runway_lock_until = max(self.runway_lock_until, now + occ)
        self.last_takeoff_time = now
        self.last_op = "T"

    def can_land(self, eta: int) -> bool:
        # zakładamy sprawdzenie na czas przylotu (ETA)
        if self.last_op == "L":
            return (eta - self.last_landing_time) >= self.sep_LL_s and eta >= self.runway_lock_until
        if self.last_op == "T":
            return (eta - self.last_takeoff_time) >= self.sep_TL_s and eta >= self.runway_lock_until
        return eta >= self.runway_lock_until

    def grant_landing(self, now_touchdown: int):
        occ = self.landing_roll_time_s + self.runway_buffer_after_exit_s
        self.runway_lock_until = max(self.runway_lock_until, now_touchdown + occ)
        self.last_landing_time = now_touchdown
        self.last_op = "L"

@dataclass
class SegmentReservation:
    """Rezerwacja segmentu lotniska"""
    segment_id: int
    airplane_id: int
    start_time: int
    end_time: int
    priority: int = 1  # Wyższa liczba = wyższy priorytet
    reservation_type: str = "movement"  # movement, holding, emergency

@dataclass
class ConflictProposal:
    """Propozycja rozwiązania konfliktu"""
    from_airplane: int
    to_airplane: int
    proposal_type: str  # "wait", "alternative_route", "priority_swap"
    details: Dict
    timestamp: int

from typing import Dict, List, Tuple, Optional


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Zapewnia deterministyczny klucz krawędzi (kolejność bez znaczenia)."""
    return (u, v) if u <= v else (v, u)


class SegmentManager:
    """Uproszczony menedżer rezerwacji segmentów lotniska."""

    def __init__(self, model=None):
        self.model = model
        # Rezerwacje krawędzi: (u,v) -> lista ID samolotów zajmujących segment
        self.edge_reservations: Dict[Tuple[int, int], List[int]] = {}
        # Rezerwacje węzłów: node_id -> ID samolotu (pojemność = 1)
        self.node_reservations: Dict[int, int] = {}
        # Prosty lock pushbacku (1 tug)
        self.pushback_lock_until: int = 0
        self.pushback_active_aircraft: Optional[int] = None
        self.default_pushback_time: int = 3  # liczba ticków pushbacku (prosty model)

    # ------------------------------------------------------------------
    # Pomocnicze
    # ------------------------------------------------------------------
    def _edge_capacity(self, u: int, v: int) -> int:
        if self.model and self.model.graph.graph.has_edge(u, v):
            capacity = self.model.graph.graph[u][v].get("capacity")
            if isinstance(capacity, int) and capacity > 0:
                return capacity
            # Jeśli to runway – domyślnie 1
            edge_type = self.model.graph.graph[u][v].get("type")
            if edge_type == "runway":
                return 1
        return 1

    # ------------------------------------------------------------------
    # Rezerwacje węzłów
    # ------------------------------------------------------------------
    def request_node(self, node_id: int, airplane_id: int) -> bool:
        owner = self.node_reservations.get(node_id)
        if owner is None or owner == airplane_id:
            self.node_reservations[node_id] = airplane_id
            return True
        return False

    def release_node(self, node_id: int, airplane_id: int):
        owner = self.node_reservations.get(node_id)
        if owner == airplane_id:
            del self.node_reservations[node_id]

    # ------------------------------------------------------------------
    # Rezerwacje krawędzi
    # ------------------------------------------------------------------
    def request_edge(self, u: int, v: int, airplane_id: int) -> bool:
        key = _edge_key(u, v)
        slots = self.edge_reservations.setdefault(key, [])
        if airplane_id in slots:
            return True
        capacity = self._edge_capacity(u, v)
        if len(slots) < capacity:
            slots.append(airplane_id)
            return True
        return False

    def release_edge(self, u: int, v: int, airplane_id: int):
        key = _edge_key(u, v)
        if key in self.edge_reservations and airplane_id in self.edge_reservations[key]:
            self.edge_reservations[key].remove(airplane_id)
            if not self.edge_reservations[key]:
                del self.edge_reservations[key]


    # ------------------------------------------------------------------
    # Rezerwacje sekcji lotniska 
    # ------------------------------------------------------------------
    def request_airport_section(self, section: str, airplane_id: int) -> Tuple[bool, List[Dict]]:
        success = True
        blocked_edges = []
        match section:
            case "runway":
                for edge in self.model.graph.get_edges_by_type("runway"):
                    if not self.request_edge(edge['from'], edge['to'], airplane_id):
                        success = False
                        break
                    else:
                        blocked_edges.append(edge)
            case "taxiway_inbound":
                success = False
                for edge in self.model.graph.get_edges_by_type("runway_entry"):
                    if self.request_edge(edge['from'], edge['to'], airplane_id):
                        success = True
                        blocked_edges.append(edge)
                        break
            case "taxiway_outbound":
                success = False
                for edge in self.model.graph.get_edges_by_type("runway_exit"):
                    if self.request_edge(edge['from'], edge['to'], airplane_id):
                        success = True
                        blocked_edges.append(edge)
                        break
            case "taxiway":
                for edge in self.model.graph.get_edges_by_type("taxiway"):
                    if not self.request_edge(edge['from'], edge['to'], airplane_id):
                        success = False
                        break
                    else:
                        blocked_edges.append(edge)
            case "apron":
                edges = self.model.graph.get_edges_by_type("apron_link")
                edges.extend(self.model.graph.get_edges_by_type("stand_link"))
                for edge in edges:
                    if not self.request_edge(edge['from'], edge['to'], airplane_id):
                        success = False
                        return False, blocked_edges
                    else:
                        blocked_edges.append(edge)
                return success, blocked_edges
            case _:
                return False, blocked_edges


        if not success:
            self.release_edges(blocked_edges, airplane_id)
            return False, blocked_edges
        return success, blocked_edges

    def release_edges(self, edges: List[Dict], airplane_id: int):
        for edge in edges:
            self.release_edge(edge['from'], edge['to'], airplane_id)
        return True

    # ------------------------------------------------------------------
    # Informacje
    # ------------------------------------------------------------------
    def get_edge_status(self, u: int, v: int) -> Dict[str, Optional[List[int]]]:
        key = _edge_key(u, v)
        occupants = self.edge_reservations.get(key, [])
        return {
            "occupied": len(occupants) > 0,
            "airplanes": occupants.copy()
        }

    def get_node_status(self, node_id: int) -> Dict[str, Optional[int]]:
        owner = self.node_reservations.get(node_id)
        return {
            "occupied": owner is not None,
            "airplane": owner
        }

    def cleanup_old_reservations(self, _current_time: int):
        """Zachowane dla kompatybilności – nic nie robi w uproszczonej wersji."""
        pass
