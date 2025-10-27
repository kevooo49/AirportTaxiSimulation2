# Symulacja Lotniska z Pasem Startowym - Mesa

Projekt symuluje ruch samolotów na lotnisku z pasem startowym przy użyciu frameworka Mesa. Symulacja zawiera różne agenty reprezentujące samoloty, model zarządzający środowiskiem symulacji oraz narzędzia wizualizacji do wyświetlania wyników.

## Struktura Projektu

- **src/**: Zawiera główny kod źródłowy symulacji.

  - **agents.py**: Definiuje klasy `Airplane` i `RunwayController` z właściwościami i metodami dla zachowania samolotów i kontroli pasa startowego.
  - **model.py**: Zawiera klasę `AirportModel` zarządzającą środowiskiem symulacji.
  - **visualization.py**: Obsługuje wizualizację symulacji z animacjami i statystykami.

- **notebooks/**: Zawiera notebooki Jupyter do eksploracyjnej analizy danych.

  - **exploration.ipynb**: Używany do analizy i wizualizacji wyników symulacji.

- **data/**: Przechowuje pliki danych związane z symulacją.

  - **runway_logs.csv**: Logi ruchów samolotów na pasie startowym.

- **tests/**: Zawiera testy jednostkowe dla projektu.

  - **test_model.py**: Testy jednostkowe dla klasy `AirportModel`.

- **requirements.txt**: Lista zależności wymaganych dla projektu.

- **run_simulation.py**: Główny plik uruchamiający symulację.
- **test_simulation.py**: Plik testowy sprawdzający podstawową funkcjonalność.

## Instrukcje Instalacji

1. Sklonuj repozytorium na swoją maszynę lokalną.
2. Przejdź do katalogu projektu.
3. Zainstaluj wymagane zależności używając:
   ```
   pip install -r requirements.txt
   ```

## Uruchamianie Symulacji

### Opcja 1: Główny skrypt

```bash
python run_simulation.py
```

Skrypt oferuje kilka opcji:

1. **Animacja interaktywna** - pokazuje animację w czasie rzeczywistym
2. **Statyczny obraz** - pokazuje jeden obraz stanu symulacji
3. **Zapisz animację** - zapisuje animację do pliku GIF
4. **Pełna symulacja** - uruchamia pełną symulację i pokazuje statystyki

### Opcja 2: Szybka demonstracja

```bash
python run_simulation.py --demo
```

### Opcja 3: Notebook Jupyter

```bash
jupyter notebook notebooks/exploration.ipynb
```

### Opcja 4: Test funkcjonalności

```bash
python test_simulation.py
```

## Przegląd Symulacji

Symulacja modeluje zachowanie samolotów podczas ich ruchu po lotnisku, zbliżania się do pasa startowego i lądowania na podstawie zdefiniowanych reguł.

### Agenty:

- **Samoloty (Airplane)**: Poruszają się po lotnisku w różnych stanach:

  - `flying` (niebieski) - lecą w kierunku pasa startowego
  - `approaching` (pomarańczowy) - zbliżają się do pasa startowego
  - `landing` (czerwony) - lądują na pasie startowym
  - `landed` (zielony) - wylądowały

- **Kontroler Pasa Startowego (RunwayController)**: Zarządza dostępem do pasa startowego, tworzy kolejkę samolotów oczekujących na lądowanie.

### Funkcje Wizualizacji:

- **Animacja w czasie rzeczywistym** z różnymi kształtami dla różnych stanów samolotów
- **Statystyki symulacji** pokazujące liczbę samolotów w każdym stanie w czasie
- **Informacje o stanie** wyświetlane na wykresie
- **Legenda** wyjaśniająca kolory i kształty

## Parametry Symulacji

Możesz dostosować parametry symulacji w pliku `run_simulation.py`:

- `width` - szerokość lotniska (domyślnie 20)
- `height` - wysokość lotniska (domyślnie 10)
- `num_airplanes` - liczba samolotów (domyślnie 5)

## Wymagania Systemowe

- Python 3.7+
- Mesa 3.3.0
- matplotlib 3.9.2
- numpy 2.3.4
- pandas 2.3.3

## Wkład w Projekt

Wkład w projekt jest mile widziany. Proszę przesłać pull request lub otworzyć issue dla wszelkich sugestii lub ulepszeń.
