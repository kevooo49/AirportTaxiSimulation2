# System Rezerwacji Segmentów i Rozwiązywania Konfliktów

## 🎯 Przegląd

Zaimplementowano zaawansowany system rezerwacji segmentów lotniska z mechanizmem rozwiązywania konfliktów między samolotami. System pozwala samolotom negocjować dostęp do segmentów, a gdy negocjacje nie przynoszą rezultatu, główny kontroler rozstrzyga konflikty.

## 🏗️ Architektura Systemu

### 1. **SegmentManager** (`src/segment_manager.py`)
Centralny zarządca rezerwacji segmentów lotniska.

#### Kluczowe funkcje:
- **Rezerwacja segmentów**: `request_segment(segment_id, airplane_id, duration, current_time)`
- **Rozwiązywanie konfliktów**: `resolve_conflict_by_controller()`
- **Zarządzanie propozycjami**: `create_conflict_proposal()`
- **Czyszczenie starych rezerwacji**: `cleanup_old_reservations()`

#### Struktury danych:
```python
@dataclass
class SegmentReservation:
    segment_id: int
    airplane_id: int
    start_time: int
    end_time: int
    priority: int = 1
    reservation_type: str = "movement"

@dataclass
class ConflictProposal:
    from_airplane: int
    to_airplane: int
    proposal_type: str
    details: Dict
    timestamp: int
```

### 2. **Rozszerzona klasa Airplane**
Dodano mechanizmy negocjacji i zarządzania konfliktami.

#### Nowe atrybuty:
```python
self.reserved_segments = []           # Lista zarezerwowanych segmentów
self.waiting_for_segment = None       # Segment na który czeka
self.conflict_proposals_sent = []     # Wysłane propozycje
self.conflict_proposals_received = [] # Otrzymane propozycje
self.priority = 1                     # Priorytet samolotu
self.wait_time = 0                    # Czas oczekiwania na segment
self.max_wait_time = 5                # Maksymalny czas oczekiwania
```

#### Nowe metody:
- `_handle_segment_conflict()` - Obsługuje konflikty dostępu
- `_create_conflict_proposal()` - Tworzy propozycje rozwiązań
- `_request_controller_arbitration()` - Prosi kontrolera o arbitraż
- `_find_alternative_route()` - Znajduje alternatywne ścieżki
- `process_conflict_proposals()` - Przetwarza otrzymane propozycje

## 🔄 Mechanizm Rozwiązywania Konfliktów

### Etap 1: Wykrycie Konfliktu
Gdy samolot próbuje zarezerwować zajęty segment:
```python
success, conflict_airplane = segment_manager.request_segment(
    next_node, airplane_id, 1, current_time
)
```

### Etap 2: Negocjacja (Jeśli równy priorytet)
Samolot wysyła propozycję rozwiązania konfliktu:

#### Typy propozycji:
1. **"wait"** - Propozycja poczekania
   ```python
   {
       "type": "wait",
       "details": {"wait_time": 2, "reason": "taxiing_priority"}
   }
   ```

2. **"alternative_route"** - Propozycja alternatywnej ścieżki
   ```python
   {
       "type": "alternative_route", 
       "details": {"reason": "departure_priority"}
   }
   ```

3. **"priority_swap"** - Propozycja zamiany priorytetów
   ```python
   {
       "type": "priority_swap",
       "details": {"new_priority": 2, "reason": "urgent_movement"}
   }
   ```

### Etap 3: Ocena Propozycji
Odbiorca ocenia propozycję:
```python
def _evaluate_proposal(self, proposal: ConflictProposal) -> bool:
    if proposal.proposal_type == "wait":
        return self.state not in ["waiting_departure", "departing"]
    elif proposal.proposal_type == "alternative_route":
        return self.target_node is not None
    # ...
```

### Etap 4: Arbitraż Kontrolera
Jeśli negocjacje nie przynoszą rezultatu po `max_wait_time` kroków:
```python
winner = segment_manager.resolve_conflict_by_controller(
    segment_id, airplane1_id, airplane2_id, current_time
)
```

## 🎮 Logika Priorytetów

### Hierarchia priorytetów:
1. **Wyższy priorytet** → automatycznie wygrywa
2. **Równy priorytet** → negocjacja
3. **Niższy priorytet** → musi poczekać

### Ustawianie priorytetów:
```python
# W modelu
segment_manager.set_airplane_priority(airplane_id, priority)

# Samoloty mogą zmieniać priorytet w zależności od stanu
if self.state == "waiting_departure":
    self.priority = 3  # Wyższy priorytet dla odlotów
elif self.state == "taxiing_to_stand":
    self.priority = 2  # Średni priorytet
else:
    self.priority = 1  # Standardowy priorytet
```

## 📊 Monitoring Konfliktów

### Statystyki dostępne w modelu:
```python
# Liczba aktywnych konfliktów
active_conflicts = len(model.segment_manager.conflict_proposals)

# Samoloty czekające na segmenty
waiting_airplanes = [p for p in model.airplanes if p.wait_time > 0]

# Status segmentu
status = segment_manager.get_segment_status(segment_id, current_time)
```

## 🧪 Testowanie Systemu

### Przykład testu:
```python
from src.model import AirportModel

model = AirportModel(num_arriving_airplanes=4, arrival_rate=0.2)

conflicts_detected = 0
for i in range(30):
    model.step()
    
    active_conflicts = len(model.segment_manager.conflict_proposals)
    if active_conflicts > 0:
        conflicts_detected += 1
        print(f"Krok {i+1}: WYKRYTO KONFLIKT! Propozycji: {active_conflicts}")

print(f"Wykryto konfliktów: {conflicts_detected}")
```

## 🎨 Wizualizacja Konfliktów

W wizualizacji można dodać:
- **Czerwone obramowanie** - samoloty w konflikcie
- **Żółte tło** - segmenty z aktywnymi rezerwacjami
- **Liczniki** - liczba aktywnych konfliktów i propozycji

## 🔧 Konfiguracja

### Parametry do dostosowania:
```python
# W klasie Airplane
self.max_wait_time = 5        # Maksymalny czas oczekiwania
self.priority = 1             # Domyślny priorytet

# W SegmentManager
max_reservation_time = 10     # Maksymalny czas rezerwacji
cleanup_interval = 5          # Częstotliwość czyszczenia
```

## 📈 Korzyści Systemu

1. **Realistyczny ruch** - Samoloty nie mogą się "teleportować"
2. **Inteligentne negocjacje** - Samoloty próbują rozwiązać konflikty samodzielnie
3. **Sprawiedliwy arbitraż** - Kontroler rozstrzyga trudne przypadki
4. **Elastyczność** - Różne strategie w zależności od sytuacji
5. **Monitoring** - Pełna widoczność konfliktów i ich rozwiązań

## 🚀 Przykład Użycia

```python
# Uruchomienie symulacji z systemem konfliktów
model = AirportModel(
    num_arriving_airplanes=5,
    wind_direction="07", 
    arrival_rate=0.15
)

# Symulacja z monitoringiem konfliktów
for step in range(100):
    model.step()
    
    # Sprawdź konflikty
    conflicts = len(model.segment_manager.conflict_proposals)
    if conflicts > 0:
        print(f"Krok {step}: {conflicts} aktywnych konfliktów")
```

System jest w pełni zintegrowany z istniejącą symulacją i działa transparentnie w tle! 🎉
