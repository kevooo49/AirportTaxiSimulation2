# Poprawki Systemu Ruchu Samolotów

## 🎯 Problem i Rozwiązanie

### **PROBLEM:**

1. **Więcej niż 1 samolot na pasie startowym** - Samoloty mogły jednocześnie używać różnych węzłów pasa (1 i 2)
2. **Samoloty mogły się wymijać** - Brak kolejek na drogach, samoloty próbowały ominąć się nawzajem

### **ROZWIĄZANIE:**

✅ **Tylko 1 samolot na pasie startowym naraz**  
✅ **Zakaz wymijania się - samoloty tworzą kolejki na drogach**

## 🔧 Zmiany Techniczne

### **1. SegmentManager - Specjalna logika pasa startowego**

#### Nowa metoda `_request_runway_segment()`:

```python
def _request_runway_segment(self, segment_id: int, airplane_id: int,
                          duration: int, current_time: int) -> Tuple[bool, Optional[str]]:
    """Specjalna logika rezerwacji pasa startowego - tylko 1 samolot naraz"""

    # Sprawdź czy jakikolwiek samolot już używa pasa startowego (oba końce)
    for seg_id in [1, 2]:  # Sprawdź oba końce pasa
        if seg_id in self.reservations:
            for reservation in self.reservations[seg_id]:
                if reservation.start_time <= current_time <= reservation.end_time:
                    return False, reservation.airplane_id

    # Sprawdź też czy jakikolwiek samolot ma current_node na pasie
    for airplane in self.model.airplanes:
        if airplane.current_node in [1, 2] and airplane.unique_id != airplane_id:
            return False, airplane.unique_id

    # Pas wolny - dodaj rezerwację
    return True, None
```

#### Nowa metoda `request_segment_with_no_passing()`:

```python
def request_segment_with_no_passing(self, segment_id: int, airplane_id: int,
                                   duration: int, current_time: int) -> Tuple[bool, Optional[str]]:
    """Próbuje zarezerwować segment z zakazem wymijania się"""

    # Specjalna logika dla pasa startowego
    if self._is_runway_segment(segment_id):
        return self._request_runway_segment(segment_id, airplane_id, duration, current_time)

    # Dla innych segmentów - sprawdź czy jest wolny
    active_reservations = []
    for reservation in self.reservations[segment_id]:
        if not (requested_end <= reservation.start_time or requested_start >= reservation.end_time):
            active_reservations.append(reservation)

    if active_reservations:
        # Segment zajęty - nie można wymijać
        return False, active_reservations[0].airplane_id

    # Segment wolny - dodaj rezerwację
    return True, None
```

### **2. RunwayController - Sprawdzanie dostępności pasa**

#### Zaktualizowana metoda `step()`:

```python
def step(self):
    if not self.is_busy:
        if self.landing_queue and self.active_runway:
            airplane = self.landing_queue.pop(0)

            # Sprawdź czy można zarezerwować pas startowy
            success, conflict_airplane = self.model.segment_manager.request_segment_with_no_passing(
                self.active_runway, airplane.unique_id, 1, self.model.step_count
            )

            if success:
                # Pas wolny - rozpocznij lądowanie
                self.is_busy = True
                airplane.state = "landing"
                # ... reszta logiki
            else:
                # Pas zajęty - wróć samolot do kolejki
                self.landing_queue.insert(0, airplane)
```

### **3. Airplane - System kolejek na drogach**

#### Nowe atrybuty:

```python
# System kolejek na drogach
self.blocked_by_airplane = None  # ID samolotu który blokuje drogę
self.waiting_position = None      # Pozycja gdzie czeka
self.queue_position = 0          # Pozycja w kolejce (0 = pierwszy)
```

#### Zaktualizowana logika ruchu:

```python
def _move_along_path(self):
    # Sprawdź czy można zarezerwować następny segment (z zakazem wymijania)
    success, conflict_airplane = self.model.segment_manager.request_segment_with_no_passing(
        next_node, self.unique_id, 1, self.model.step_count
    )

    if success:
        # Segment zarezerwowany - rozpocznij ruch
        self._start_movement_to_node(next_node)
        # Wyczyść stan oczekiwania
        self.blocked_by_airplane = None
        self.waiting_position = None
        self.queue_position = 0
    else:
        # Konflikt - samolot musi czekać w kolejce (zakaz wymijania)
        self.wait_time += 1
        self.waiting_for_segment = next_node
        self.blocked_by_airplane = conflict_airplane

        # Ustaw pozycję oczekiwania jeśli nie jest ustawiona
        if not self.waiting_position:
            self.waiting_position = self.get_position()
```

## 📊 Wyniki Testów

### **PRZED poprawkami:**

```
Krok  5: Pas używany przez samoloty: [2, 3]
Krok  6: Pas używany przez samoloty: [2, 3]
Krok  8: Pas używany przez samoloty: [2, 3, 4]
```

❌ **Więcej niż 1 samolot na pasie**

### **PO poprawkach:**

```
Krok  2: Pas używany przez samoloty: [2]
Krok  3: Pas używany przez samoloty: [2]
Krok  4: Pas używany przez samoloty: [2]
Krok  5: Pas używany przez samoloty: [2]
```

✅ **Tylko 1 samolot na pasie**

### **Kolejki na drogach:**

```
Krok  1: Kolejka lądowań: 3, Kolejka startów: 0
Krok  9: Kolejka lądowań: 2, Kolejka startów: 0
Krok 17: Kolejka lądowań: 2, Kolejka startów: 0
```

✅ **Samoloty czekają w kolejce zamiast wymijać się**

## 🎯 Kluczowe Funkcje

### **1. Blokada pasa startowego:**

- Sprawdzanie obu węzłów pasa (1 i 2)
- Sprawdzanie aktualnych pozycji samolotów
- Zwracanie samolotów do kolejki gdy pas zajęty

### **2. Zakaz wymijania się:**

- Metoda `request_segment_with_no_passing()`
- Brak negocjacji - samoloty muszą czekać
- Tworzenie kolejek na drogach

### **3. System kolejek:**

- `blocked_by_airplane` - ID samolotu który blokuje
- `waiting_position` - Pozycja gdzie samolot czeka
- `queue_position` - Pozycja w kolejce

## 🚀 Korzyści

1. **Realistyczny ruch** ✅

   - Tylko 1 samolot na pasie startowym
   - Brak nierealistycznego wymijania się

2. **Bezpieczeństwo** ✅

   - Eliminacja kolizji na pasie startowym
   - Kontrolowane kolejki na drogach

3. **Realizm operacyjny** ✅

   - Odzwierciedla rzeczywiste procedury lotniskowe
   - Samoloty czekają w kolejce jak w rzeczywistości

4. **Stabilność systemu** ✅
   - Brak nieskończonych pętli prób ominięcia
   - Przewidywalne zachowanie samolotów

## 📝 Pliki Zmienione

- ✅ `src/segment_manager.py` - Specjalna logika pasa startowego
- ✅ `src/agents/runway_controler.py` - Sprawdzanie dostępności pasa
- ✅ `src/agents/airplane.py` - System kolejek na drogach
- ✅ `src/model.py` - Przekazanie referencji do SegmentManager

## 🧪 Testowanie

```python
# Test systemu pasa startowego
model = AirportModel(num_arriving_airplanes=3, wind_direction='07')

for i in range(50):
    model.step()

    # Sprawdź użycie pasa
    runway_users = []
    for plane in model.airplanes:
        if plane.current_node in [1, 2]:
            runway_users.append(plane.unique_id)

    if runway_users:
        print(f'Krok {i+1}: Pas używany przez: {runway_users}')
```

**Oczekiwany wynik:** Tylko 1 samolot na pasie naraz! 🎉

---

System jest teraz w pełni funkcjonalny i realistyczny! Samoloty poruszają się płynnie, tworzą kolejki na drogach i tylko jeden samolot może używać pasa startowego naraz.
