import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ConflictResolution(Enum):
    """Typy rozwiązań konfliktów"""
    FIRST_COME_FIRST_SERVED = "first_come_first_served"
    PRIORITY_BASED = "priority_based"
    NEGOTIATION = "negotiation"
    CONTROLLER_DECISION = "controller_decision"

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

class SegmentManager:
    """Zarządza rezerwacjami segmentów lotniska i rozwiązywaniem konfliktów"""
    
    def __init__(self, model=None):
        self.reservations: Dict[int, List[SegmentReservation]] = {}  # segment_id -> reservations
        self.conflict_proposals: List[ConflictProposal] = []
        self.airplane_priorities: Dict[int, int] = {}  # airplane_id -> priority
        self.reservation_counter = 0
        self.model = model  # Referencja do modelu
        
    def set_airplane_priority(self, airplane_id: int, priority: int):
        """Ustawia priorytet samolotu"""
        self.airplane_priorities[airplane_id] = priority
    
    def request_segment(self, segment_id: int, airplane_id: int, 
                       duration: int, current_time: int) -> Tuple[bool, Optional[str]]:
        """
        Próbuje zarezerwować segment lotniska
        
        Returns:
            (success, conflict_airplane_id) - czy udało się zarezerwować i ID samolotu w konflikcie
        """
        # Specjalna logika dla pasa startowego - tylko 1 samolot naraz
        if self._is_runway_segment(segment_id):
            return self._request_runway_segment(segment_id, airplane_id, duration, current_time)
        
        if segment_id not in self.reservations:
            self.reservations[segment_id] = []
        
        # Sprawdź czy segment jest wolny w danym czasie
        requested_start = current_time
        requested_end = current_time + duration
        
        for reservation in self.reservations[segment_id]:
            # Sprawdź czy rezerwacje się nakładają
            if not (requested_end <= reservation.start_time or requested_start >= reservation.end_time):
                # Konflikt! Sprawdź priorytety
                airplane_priority = self.airplane_priorities.get(airplane_id, 1)
                reservation_priority = self.airplane_priorities.get(reservation.airplane_id, 1)
                
                if airplane_priority > reservation_priority:
                    # Wyższy priorytet - usuń starą rezerwację
                    self.reservations[segment_id].remove(reservation)
                    break
                elif airplane_priority < reservation_priority:
                    # Niższy priorytet - nie można zarezerwować
                    return False, reservation.airplane_id
                else:
                    # Równy priorytet - potrzebna negocjacja
                    return False, reservation.airplane_id
        
        # Segment wolny - dodaj rezerwację
        reservation = SegmentReservation(
            segment_id=segment_id,
            airplane_id=airplane_id,
            start_time=requested_start,
            end_time=requested_end,
            priority=self.airplane_priorities.get(airplane_id, 1)
        )
        self.reservations[segment_id].append(reservation)
        self.reservation_counter += 1
        
        return True, None
    
    def _is_runway_segment(self, segment_id: int) -> bool:
        """Sprawdza czy segment jest częścią pasa startowego"""
        # Węzły pasa startowego: 1 (RWY_07), 2 (RWY_25)
        return segment_id in [1, 2]
    
    def _request_runway_segment(self, segment_id: int, airplane_id: int, 
                              duration: int, current_time: int) -> Tuple[bool, Optional[str]]:
        """Specjalna logika rezerwacji pasa startowego - tylko 1 samolot naraz"""
        # Sprawdź czy jakikolwiek samolot już używa pasa startowego (oba końce)
        for seg_id in [1, 2]:  # Sprawdź oba końce pasa
            if seg_id in self.reservations:
                for reservation in self.reservations[seg_id]:
                    # Sprawdź czy rezerwacja jest aktywna
                    if reservation.start_time <= current_time <= reservation.end_time:
                        return False, reservation.airplane_id
        
        # Sprawdź też czy jakikolwiek samolot ma current_node na pasie
        for airplane in self.model.airplanes:
            if airplane.current_node in [1, 2] and airplane.unique_id != airplane_id:
                return False, airplane.unique_id
        
        # Pas wolny - dodaj rezerwację
        if segment_id not in self.reservations:
            self.reservations[segment_id] = []
        
        reservation = SegmentReservation(
            segment_id=segment_id,
            airplane_id=airplane_id,
            start_time=current_time,
            end_time=current_time + duration,
            priority=self.airplane_priorities.get(airplane_id, 1)
        )
        self.reservations[segment_id].append(reservation)
        self.reservation_counter += 1
        
        return True, None
    
    def request_segment_with_no_passing(self, segment_id: int, airplane_id: int, 
                                       duration: int, current_time: int) -> Tuple[bool, Optional[str]]:
        """
        Próbuje zarezerwować segment z zakazem wymijania się
        Samoloty muszą czekać w kolejce na drogach
        """
        # Specjalna logika dla pasa startowego
        if self._is_runway_segment(segment_id):
            return self._request_runway_segment(segment_id, airplane_id, duration, current_time)
        
        if segment_id not in self.reservations:
            self.reservations[segment_id] = []
        
        # Sprawdź czy segment jest wolny
        requested_start = current_time
        requested_end = current_time + duration
        
        # Znajdź wszystkie aktywne rezerwacje dla tego segmentu
        active_reservations = []
        for reservation in self.reservations[segment_id]:
            if not (requested_end <= reservation.start_time or requested_start >= reservation.end_time):
                active_reservations.append(reservation)
        
        if active_reservations:
            # Segment zajęty - nie można wymijać
            return False, active_reservations[0].airplane_id
        
        # Segment wolny - dodaj rezerwację
        reservation = SegmentReservation(
            segment_id=segment_id,
            airplane_id=airplane_id,
            start_time=requested_start,
            end_time=requested_end,
            priority=self.airplane_priorities.get(airplane_id, 1)
        )
        self.reservations[segment_id].append(reservation)
        self.reservation_counter += 1
        
        return True, None
    
    def release_segment(self, segment_id: int, airplane_id: int, current_time: int):
        """Zwolnij segment lotniska"""
        if segment_id in self.reservations:
            self.reservations[segment_id] = [
                r for r in self.reservations[segment_id] 
                if not (r.airplane_id == airplane_id and r.start_time <= current_time <= r.end_time)
            ]
    
    def create_conflict_proposal(self, from_airplane: int, to_airplane: int, 
                               proposal_type: str, details: Dict, current_time: int):
        """Tworzy propozycję rozwiązania konfliktu"""
        proposal = ConflictProposal(
            from_airplane=from_airplane,
            to_airplane=to_airplane,
            proposal_type=proposal_type,
            details=details,
            timestamp=current_time
        )
        self.conflict_proposals.append(proposal)
        return proposal
    
    def get_conflict_proposals_for_airplane(self, airplane_id: int) -> List[ConflictProposal]:
        """Pobiera propozycje konfliktów dla danego samolotu"""
        return [p for p in self.conflict_proposals if p.to_airplane == airplane_id]
    
    def resolve_conflict_by_controller(self, segment_id: int, airplane1: int, 
                                     airplane2: int, current_time: int) -> int:
        """
        Kontroler rozstrzyga konflikt
        Returns: ID samolotu który wygrywa
        """
        priority1 = self.airplane_priorities.get(airplane1, 1)
        priority2 = self.airplane_priorities.get(airplane2, 1)
        
        if priority1 > priority2:
            winner = airplane1
        elif priority2 > priority1:
            winner = airplane2
        else:
            # Równy priorytet - pierwszy który zgłosił
            winner = airplane1  # Można dodać bardziej zaawansowaną logikę
        
        # Usuń przegraną rezerwację
        if segment_id in self.reservations:
            self.reservations[segment_id] = [
                r for r in self.reservations[segment_id] 
                if not (r.airplane_id != winner and r.start_time <= current_time <= r.end_time)
            ]
        
        return winner
    
    def cleanup_old_reservations(self, current_time: int):
        """Usuwa stare rezerwacje"""
        for segment_id in self.reservations:
            self.reservations[segment_id] = [
                r for r in self.reservations[segment_id] 
                if r.end_time > current_time
            ]
    
    def get_segment_status(self, segment_id: int, current_time: int) -> Dict:
        """Zwraca status segmentu"""
        if segment_id not in self.reservations:
            return {"status": "free", "reserved_by": None}
        
        for reservation in self.reservations[segment_id]:
            if reservation.start_time <= current_time <= reservation.end_time:
                return {
                    "status": "occupied", 
                    "reserved_by": reservation.airplane_id,
                    "until": reservation.end_time
                }
        
        return {"status": "free", "reserved_by": None}
