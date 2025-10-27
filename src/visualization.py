import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


class AirportVisualization:
    """Wizualizacja symulacji lotniska"""
    
    def __init__(self, model):
        self.model = model
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.setup_plot()
        
    def setup_plot(self):
        """Konfiguracja wykresu"""
        self.ax.set_xlim(0, self.model.width)
        self.ax.set_ylim(0, self.model.height)
        self.ax.set_aspect('equal')
        self.ax.set_title('Symulacja Lotniska - Pas Startowy', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('Pozycja X', fontsize=12)
        self.ax.set_ylabel('Pozycja Y', fontsize=12)
        
        # Rysowanie pasa startowego
        runway_y = self.model.height // 2
        runway_width = self.model.width
        runway_height = 3
        
        runway = Rectangle((0, runway_y - 1), runway_width, runway_height, 
                          facecolor='gray', edgecolor='black', linewidth=2, alpha=0.7)
        self.ax.add_patch(runway)
        
        # Dodanie etykiet pasa startowego
        self.ax.text(self.model.width/2, runway_y, 'PAS STARTOWY', 
                    ha='center', va='center', fontsize=14, fontweight='bold', 
                    color='white', bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Legenda
        legend_elements = [
            mpatches.Patch(color='blue', label='Samoloty w locie'),
            mpatches.Patch(color='orange', label='Zbliżające się'),
            mpatches.Patch(color='red', label='Lądujące'),
            mpatches.Patch(color='green', label='Wylądowane'),
            mpatches.Patch(color='gray', label='Pas startowy')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
        
        # Siatka
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xticks(range(0, self.model.width + 1))
        self.ax.set_yticks(range(0, self.model.height + 1))
        
    def render(self):
        """Renderowanie aktualnego stanu symulacji"""
        self.ax.clear()
        self.setup_plot()
        
        # Rysowanie samolotów
        for agent in self.model.agents:
            if hasattr(agent, 'get_color'):  # To jest samolot
                x, y = agent.pos
                color = agent.get_color()
                size = 200 if agent.state == "landing" else 150
                
                # Różne kształty dla różnych stanów
                if agent.state == "flying":
                    marker = '^'  # Trójkąt
                elif agent.state == "approaching":
                    marker = 's'  # Kwadrat
                elif agent.state == "landing":
                    marker = 'o'  # Koło
                else:  # landed
                    marker = 'D'  # Diament
                
                self.ax.scatter(x, y, c=color, s=size, marker=marker, 
                              edgecolors='black', linewidth=1, alpha=0.8)
                
                # Etykieta z ID samolotu
                self.ax.annotate(f'A{agent.unique_id}', (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, fontweight='bold')
        
        # Informacje o stanie
        info_text = f"Krok: {self.model.steps}\n"
        info_text += f"Samoloty w locie: {len([a for a in self.model.agents if hasattr(a, 'state') and a.state == 'flying'])}\n"
        info_text += f"Zbliżające się: {len([a for a in self.model.agents if hasattr(a, 'state') and a.state == 'approaching'])}\n"
        info_text += f"Lądujące: {len([a for a in self.model.agents if hasattr(a, 'state') and a.state == 'landing'])}\n"
        info_text += f"Wylądowane: {len([a for a in self.model.agents if hasattr(a, 'state') and a.state == 'landed'])}\n"
        info_text += f"Pas zajęty: {'TAK' if self.model.runway_controller.is_busy else 'NIE'}"
        
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
    
    def animate(self, frames=100, interval=500):
        """Animacja symulacji"""
        def animate_frame(frame):
            if self.model.running:
                self.model.step()
            self.render()
            return []
        
        anim = animation.FuncAnimation(self.fig, animate_frame, frames=frames, 
                                     interval=interval, blit=False, repeat=False)
        return anim
    
    def show_static(self):
        """Pokazanie statycznego obrazu"""
        self.render()
        plt.show()
    
    def save_animation(self, filename="airport_simulation.gif", frames=100, interval=500):
        """Zapisanie animacji do pliku"""
        anim = self.animate(frames=frames, interval=interval)
        anim.save(filename, writer='pillow', fps=2)
        print(f"Animacja zapisana jako {filename}")

