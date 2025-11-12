### Zasady symulacji lotniska (wersja MVP)

Ten dokument opisuje zasady operacyjne zaimplementowane w symulacji oraz sposób ich konfiguracji.

## Założenia ogólne

- Wszystkie samoloty są identyczne (wspólne parametry prędkości i czasów).
- Brak warunków pogodowych (brak LVP, de-icing, itp.).
- Stały kierunek wiatru wybierany przy starcie symulacji; determinuje aktywny kierunek pasa.
- Lotnisko jest modelowane jako graf z:
  - segmentami (`apron`, `taxiway`, `runway`, `queue`, `stand_link`, `apron_link`),
  - węzłami (`runway_thr`, `taxiway`, `apron`, `stand`, `connector`),
  - obsługą jednokierunkowości oraz punktami konfliktów.

## Pchanie (pushback) i apron

- Pushback wymaga globalnego zasobu „tug” (liczba: 1).
- W danym momencie tylko jeden samolot może być wypychany (globalna blokada pushbacku/apronu).
- Czas pushbacku: stały (domyślnie 90 s).
- Samolot przechodzi stany: `at_stand → pushback_pending → pushback → taxiing_to_runway`.

## Ruch po drogach kołowania (taxi)

- Jednokierunkowość: wybrane krawędzie są jednokierunkowe i są respektowane przy planowaniu trasy.
- Ograniczenie prędkości:
  - Na prostych: domyślnie 20 kt.
  - Na zakrętach: domyślnie 10 kt.
- Brak wyprzedzania na wspólnym segmencie: rezerwacja krawędzi `request_edge_with_no_passing`.
- Kolejki:
  - Segmenty typu `queue` mogą mieć pojemność (liczba statków).
  - Pojemność ogranicza liczbę równoległych rezerwacji w danym oknie czasu.
- Minimalny odstęp na taxi (headway): parametryzowalny (w metrach → odwzorowane przez czasy przejazdu i pojemność).
- Punkty konfliktów (skrzyżowania, przecięcia z pasem) są rezerwowane na okno przejazdu; równoległe przejazdy przez ten sam punkt są blokowane.

## Pas startowy (runway) i ATC

- Fazy i blokady:
  - Line-up and wait: krótkotrwała blokada pasa (domyślnie 20 s).
  - Start (takeoff roll): blokada pasa równoważna czasowi rozbiegu (domyślnie 35 s) + bufor wyjścia (15 s).
  - Lądowanie (landing roll): blokada pasa równoważna czasowi do opuszczenia pasa (domyślnie 40 s) + bufor (15 s).
- Separacje czasowe (proste stałe, bez wake turbulence klas):
  - Start po starcie (T/T): 60 s
  - Lądowanie po lądowaniu (L/L): 70 s
  - Lądowanie po starcie (L/T): 90 s
  - Start po lądowaniu (T/L): 90 s
- Zabroniony wjazd na pas, jeśli trwa blokada (`runway_lock_until`).

## Planowanie tras

- Trasy wyznaczane są w oparciu o graf skierowany, który respektuje jednokierunkowość.
- Wyszukiwanie ścieżek:
  - Najkrótsza ścieżka: `AirportGraph.find_shortest_path` (DiGraph, waga = długość).
  - Alternatywne ścieżki: `AirportGraph.find_all_paths` (z limitem długości).

## Zasady oczekiwania

- Dozwolone oczekiwanie: gate/stand (stand_link), taxiway: A, C, D, F, punkty `runway_entry` (hold short).
- Niedozwolone oczekiwanie: runway, taxiway B, `runway_exit`, apron.
- Samolot, który nie uzyska rezerwacji segmentu/węzła, pozostaje w miejscu i próbuje ponownie w kolejnym kroku.

## Rezerwacje i blokady

- Rezerwacje węzłów: tylko jeden samolot w węźle w danym czasie (kto pierwszy, ten lepszy).
- Rezerwacje krawędzi: liczba równoczesnych rezerwacji wynika z atrybutu `capacity` (domyślnie 1).
- `SegmentManager` nie negocjuje konfliktów – próba rezerwacji niepowodzeniem oznacza czekanie i ponowienie w następnym kroku.
- `request_edge`/`release_edge` i `request_node`/`release_node` to jedyne wymagane operacje.
- Punkty konfliktu:
  - `AirportGraph.add_conflict_point` pozwala oznaczyć węzły/krawędzie jako konfliktowe.
  - `SegmentManager` blokuje takie punkty na czas przejazdu.

## Stany samolotu (główne)

- Przylot: `waiting_landing → landing → taxiing_to_stand → at_stand`
- Odlot: `at_stand → pushback_pending → pushback → taxiing_to_runway → waiting_departure → departing`
- Ruch między węzłami jest interpolowany; czasy ruchu wynikają z odległości i typu segmentu.

## Parametry domyślne (skrót)

- Taxi: prosty 20 kt, zakręt 10 kt
- Headway (min odstęp): 100 m (odwzorowane w czasie/pojemności)
- Pushback: 90 s
- Line-up: 20 s
- Rozbieg: 35 s
- Lądowanie (do zjazdu): 40 s
- Bufor po opuszczeniu pasa: 15 s
- Separacje RWY: T/T 60 s, L/L 70 s, T/L 90 s, L/T 90 s

Parametry są dostępne w `src/model.py` jako `DEFAULTS` i mogą być dalej wykorzystane w komponentach kontroli ruchu.

## Konfiguracja

- Jednokierunkowość, pojemności i punkty konfliktów można ustawić w hooku:
  - `run_simulation.py → configure_airport(model)`
  - Przykładowe metody:
    - `model.graph.set_one_way(u, v, 'AB'|'BA')`
    - `model.graph.set_edge_capacity(u, v, capacity:int)`
    - `model.graph.set_edge_speed_limits(u, v, straight_kts, turn_kts)`
    - `model.graph.add_conflict_point(conflict_id, description, nodes=[...], edges=[(u,v), ...])`

## Ograniczenia i następne kroki

- Brak wake turbulence i kategorii masy – separacje są stałe dla wszystkich operacji.
- Brak LVP/pogody – brak dodatkowych buforów i ograniczeń w strefie ILS.
- Brak dynamicznego zamykania segmentów (NOTAM/prace) – można dodać poprzez wyłączenie krawędzi w grafie.
- Integrację prostego `AtcController` z kolejkami `RunwayController` można rozszerzyć wg potrzeb.
