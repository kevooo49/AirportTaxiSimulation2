#!/usr/bin/env python3
"""
Skrypt do uruchomienia animacji symulacji lotniska w czasie rzeczywistym
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.model import AirportModel
from src.visualization import AirportVisualization
import matplotlib.pyplot as plt

def run_realtime_animation():
    """Uruchamia animację w czasie rzeczywistym"""
    print("🎬 Uruchamianie animacji symulacji lotniska w czasie rzeczywistym...")
    
    # Parametry symulacji
    width = 20
    height = 20
    num_airplanes = 10
    
    print(f"Parametry:")
    print(f"- Rozmiar lotniska: {width}x{height}")
    print(f"- Liczba samolotów: {num_airplanes}")
    print(f"- Prędkość animacji: 500ms między klatkami")
    print()
    
    # Tworzenie modelu i wizualizacji
    model = AirportModel(width=width, height=height, num_airplanes=num_airplanes)
    viz = AirportVisualization(model)
    
    print("🎨 Animacja gotowa! Zamknij okno aby zakończyć.")
    print("Obserwuj jak samoloty:")
    print("- 🟦 Niebieskie trójkąty: lecą w kierunku pasa startowego")
    print("- 🟧 Pomarańczowe kwadraty: zbliżają się do pasa startowego")
    print("- 🔴 Czerwone koła: lądują na pasie startowym")
    print("- 🟢 Zielone diamenty: wylądowały")
    print()
    
    # Uruchomienie animacji
    anim = viz.animate(frames=200, interval=1000)  # 500ms między klatkami
    plt.show()
    
    print("✅ Animacja zakończona!")

if __name__ == "__main__":
    run_realtime_animation()
