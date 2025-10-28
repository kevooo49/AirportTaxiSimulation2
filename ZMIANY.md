# Zmiany w Symulacji Lotniska

## Podsumowanie zmian

Symulacja została przeprojektowana aby była bardziej realistyczna zgodnie z zasadami:

### 1. ✅ System kierunku wiatru i wyboru pasa startowego
- Dodano parametr `wind_direction` ("07" lub "25") w modelu
- Pas startowy jest wybierany automatycznie na podstawie kierunku wiatru
- RWY_07 (węzeł 1) dla wiatru "07"
- RWY_25 (węzeł 2) dla wiatru "25"

### 2. ✅ Poprawiony cykl życia samolotu
Samoloty teraz przechodzą przez kompletny cykl:

1. **waiting_landing** - samolot przybywa, oczekuje w kolejce do lądowania (w powietrzu)
2. **landing** - samolot ląduje (3 kroki)
3. **taxiing_to_stand** - taxi do stanowiska postojowego
4. **at_stand** - obsługa na stanowisku (10 kroków)
5. **taxiing_to_runway** - taxi do pasa startowego
6. **waiting_departure** - oczekiwanie w kolejce na start
7. **departing** - start (3 kroki)
8. **USUNIĘCIE** - po odlocie samolot jest usuwany z symulacji

### 3. ✅ Usuwanie samolotów po odlocie
- Po zakończeniu startu samolot jest automatycznie usuwany z symulacji
- Zgodnie z zasadą: "po tym jak samolot odleci już mnie nie interesuje"

### 4. ✅ Kolejka samolotów oczekujących na lądowanie
- Samoloty przybywające dodają się do kolejki lądowania
- Pas startowy obsługuje najpierw lądowania (priorytet), potem starty
- Jest też kolejka startów dla samolotów gotowych do odlotu

### 5. ✅ Generowanie nowych samolotów
- Nowe samoloty przybywające pojawiają się losowo z prawdopodobieństwem `arrival_rate`
- Parametr można dostosować (domyślnie 0.1 = 10% szans na nowy samolot w każdym kroku)

### 6. ✅ Ruch po płycie lotniska
- Samoloty poruszają się po grafie lotniska używając algorytmu najkrótszej ścieżki
- Sprawdzają czy węzły są wolne przed przejściem
- Automatycznie wybierają wolne stanowiska postojowe

## Zmiany w plikach

### `src/agents/airplane.py`
- Dodano nowe stany samolotu
- Zaimplementowano kompletny cykl życia
- Dodano metody: `choose_stand()`, `at_stand_service()`, `wait_for_departure()`, `depart()`

### `src/agents/runway_controler.py`
- Dodano system kierunku wiatru
- Obsługa dwóch kolejek: lądowania i startów
- Priorytet dla lądowań
- Automatyczny wybór aktywnego pasa na podstawie wiatru

### `src/model.py`
- Nowe parametry: `wind_direction`, `arrival_rate`, `num_arriving_airplanes`
- Generowanie nowych przylotów w każdym kroku
- Samoloty zaczynają "w powietrzu" (bez pozycji)

### `src/visualization.py`
- Zaktualizowana legenda ze wszystkimi stanami
- Samoloty oczekujące w powietrzu wyświetlane po lewej stronie
- Rozszerzone informacje o stanie symulacji

### `edges.csv`
- Dodano połączenia między pasem startowym a taxiways (runway_exit)
- Dodano połączenia między apron a connectorami stanowisk
- Połączono wszystkie stanowiska z główną siecią

## Parametry symulacji

### W `run_simulation.py`:
```python
num_arriving_airplanes = 5  # Początkowa liczba samolotów przybywających
wind_direction = "07"        # Kierunek wiatru: "07" lub "25"
arrival_rate = 0.1           # Prawdopodobieństwo nowego samolotu (0.0-1.0)
```

## Uruchomienie

```bash
# Tryb interaktywny
python run_simulation.py

# Szybka demonstracja
python run_simulation.py --demo
```

## Kolory stanów w wizualizacji

- 🔵 **Niebieski** - oczekujące na lądowanie
- 🔴 **Czerwony** - lądujące
- 🟠 **Pomarańczowy** - taxi do stanowiska
- 🟢 **Zielony** - na stanowisku (obsługa)
- 🟡 **Żółty** - taxi do pasa startowego
- 🟣 **Fioletowy** - oczekujące na start
- 🟪 **Magenta** - startujące

## Przykładowa symulacja

```
Krok  1: Sam:  5 | Oczek.lądow: 5, Ląduj: 0, Na stanow.: 0, Start: 0
Krok 10: Sam:  5 | Oczek.lądow: 1, Ląduj: 1, Na stanow.: 3, Start: 0
Krok 20: Sam:  6 | Oczek.lądow: 1, Ląduj: 0, Na stanow.: 2, Start: 1
Krok 30: Sam:  4 | Oczek.lądow: 2, Ląduj: 1, Na stanow.: 1, Start: 0
```

Samoloty dynamicznie przybywają, lądują, są obsługiwane i odlatują!

