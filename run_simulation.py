#!/usr/bin/env python3
"""
Główny plik uruchamiający symulację lotniska z pasem startowym
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.model import AirportModel
from src.visualization import AirportVisualization
import matplotlib.pyplot as plt


def main():
    """Główna funkcja uruchamiająca symulację"""
    print("🛫 Uruchamianie symulacji lotniska z pasem startowym...")
    print("=" * 50)
    
    # Parametry symulacji
    width = 20
    height = 10
    num_airplanes = 5
    
    print(f"Parametry symulacji:")
    print(f"- Rozmiar lotniska: {width}x{height}")
    print(f"- Liczba samolotów: {num_airplanes}")
    print()
    
    # Tworzenie modelu
    model = AirportModel(width=width, height=height, num_airplanes=num_airplanes)
    
    # Tworzenie wizualizacji
    viz = AirportVisualization(model)
    
    print("Wybierz tryb uruchomienia:")
    print("1. Animacja interaktywna")
    print("2. Statyczny obraz")
    print("3. Zapisz animację do pliku")
    print("4. Uruchom pełną symulację i pokaż statystyki")
    
    choice = input("Twój wybór (1-4): ").strip()
    
    if choice == "1":
        print("Uruchamianie animacji interaktywnej...")
        print("Zamknij okno aby zakończyć.")
        anim = viz.animate(frames=200, interval=500)
        plt.show()
        
    elif choice == "2":
        print("Pokazywanie statycznego obrazu...")
        viz.show_static()
        
    elif choice == "3":
        filename = input("Nazwa pliku (domyślnie: airport_simulation.gif): ").strip()
        if not filename:
            filename = "airport_simulation.gif"
        print(f"Zapisywanie animacji jako {filename}...")
        viz.save_animation(filename, frames=100, interval=500)
        
    elif choice == "4":
        print("Uruchamianie pełnej symulacji...")
        max_steps = 100
        
        # Uruchomienie symulacji
        step_count = 0
        while model.running and step_count < max_steps:
            model.step()
            step_count += 1
            
            if step_count % 10 == 0:
                print(f"Krok {step_count}: Samoloty w locie: {len([a for a in model.agents if hasattr(a, 'state') and a.state == 'flying'])}")
        
        print(f"\nSymulacja zakończona po {step_count} krokach.")
        
        # Pokazanie końcowych statystyk
        print("Końcowe statystyki:")
        flying = len([a for a in model.agents if hasattr(a, 'state') and a.state == 'flying'])
        landing = len([a for a in model.agents if hasattr(a, 'state') and a.state == 'landing'])
        landed = len([a for a in model.agents if hasattr(a, 'state') and a.state == 'landed'])
        print(f"- Samoloty w locie: {flying}")
        print(f"- Samoloty lądujące: {landing}")
        print(f"- Samoloty wylądowane: {landed}")
        print(f"- Pas zajęty: {'TAK' if model.runway_controller.is_busy else 'NIE'}")
        
        # Pokazanie końcowego stanu
        print("Pokazywanie końcowego stanu...")
        viz.show_static()
        
    else:
        print("Nieprawidłowy wybór. Uruchamianie domyślnej animacji...")
        anim = viz.animate(frames=100, interval=500)
        plt.show()
    
    print("\n✅ Symulacja zakończona!")


def demo_quick():
    """Szybka demonstracja symulacji"""
    print("🚀 Szybka demonstracja symulacji lotniska...")
    
    # Tworzenie modelu
    model = AirportModel(width=15, height=8, num_airplanes=3)
    
    # Tworzenie wizualizacji
    viz = AirportVisualization(model)
    
    # Uruchomienie kilku kroków
    print("Uruchamianie 20 kroków symulacji...")
    for i in range(20):
        model.step()
        print(f"Krok {i+1}: Samoloty w locie: {len([a for a in model.agents if hasattr(a, 'state') and a.state == 'flying'])}")
    
    # Pokazanie końcowego stanu
    viz.show_static()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_quick()
    else:
        main()
