import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any

class AirportGraph:
    """
    Klasa reprezentująca strukturę lotniska jako graf
    """
    
    def __init__(self, nodes_file: str, edges_file: str):
        """
        Inicjalizacja grafu lotniska z plików CSV
        
        Args:
            nodes_file: ścieżka do pliku nodes.csv
            edges_file: ścieżka do pliku edges.csv
        """
        self.nodes_df = pd.read_csv(nodes_file)
        self.edges_df = pd.read_csv(edges_file)
        
        # Nieskierowany graf do przechowywania pełnych danych geometrycznych/atr.
        self.graph = nx.Graph()
        # Skierowany graf do planowania tras (respektuje jednokierunkowość)
        self.digraph = nx.DiGraph()
        # Słownik punktów konfliktów: id -> lista (u,v) lub node_id
        self.conflict_points: Dict[int, Dict[str, Any]] = {}
        
        # Dodawanie węzłów
        for _, node in self.nodes_df.iterrows():
            self.graph.add_node(
                node['id'],
                type=node['type'],
                name=node['name'],
                x=node['x'],
                y=node['y'],
                notes=node['notes']
            )
            # Węzły również w digraph (dla spójności)
            self.digraph.add_node(node['id'])
        
        # Dodawanie krawędzi - wszystkie jako dwukierunkowe
        for _, edge in self.edges_df.iterrows():
            u = int(edge['from'])
            v = int(edge['to'])
            
            # Sprawdź czy węzły istnieją
            if u not in self.graph.nodes or v not in self.graph.nodes:
                continue
            
            edge_type = edge.get('type', 'taxiway')
            length = float(edge.get('length', 0.0))
            desc = str(edge.get('desc', '')).strip().lower()

            # Klasyfikacja miejsc oczekiwania
            # Dozwolone: gate/stand_link, "taxiway a/c/d/f", "runway_entry" (hold short), powietrze (poza grafem)
            # Zabronione: apron (brak w CSV jako typ), runway, "taxiway b", "runway_exit"
            def is_holding_allowed_local(edge_type: str, desc: str) -> bool:
                if edge_type in ('stand_link',):
                    return True
                if edge_type in ('runway', 'runway_exit'):
                    return False
                if edge_type == 'runway_entry':
                    return True
                # taxiway
                if 'taxiway b' in desc:
                    return False
                if any(x in desc for x in ['taxiway a', 'taxiway c', 'taxiway d', 'taxiway f']):
                    return True
                # Fallback: zwykły taxiway dozwolony
                if edge_type == 'taxiway':
                    return True
                return False

            # Atrybuty rozszerzone na krawędzi w grafie nieskierowanym
            self.graph.add_edge(
                u,
                v,
                type=edge_type,
                segment_type=edge_type,  # spójność nazewnicza
                length=length,
                bidirectional=True,  # Zawsze True
                one_way=False,  # Zawsze False
                allowed_dir='AB_BA',  # Zawsze oba kierunki
                capacity=None,  # liczba samolotów (opcjonalnie)
                speed_limit_straight_kts=None,
                speed_limit_turn_kts=None,
                conflict_points=[],  # lista ID punktów konfliktów związanych z tą krawędzią
                runway_exit_class=None,  # {first, middle, last} dla zjazdów z pasa
                desc=desc,
                holding_allowed=is_holding_allowed_local(edge_type, desc)
            )

            # Wszystkie krawędzie dodawane w obu kierunkach do digraph
            self.digraph.add_edge(u, v, type=edge_type, length=length, desc=desc)
            self.digraph.add_edge(v, u, type=edge_type, length=length, desc=desc)
    
    def get_node_by_id(self, node_id: int) -> Optional[Dict]:
        """Pobiera węzeł po ID"""
        if node_id in self.graph.nodes:
            return self.graph.nodes[node_id]
        return None
    
    def get_edges_by_type(self, edge_type: str) -> List[Dict]:
        """Pobiera krawędzie po typie"""
        edges = []
        for _, row in self.edges_df.iterrows():
            if row.get('type') == edge_type:
                edges.append({
                    'from': int(row['from']),
                    'to': int(row['to']),
                    'type': row.get('type', ''),
                    'length': float(row.get('length', 0.0))
                })
        return edges
    
    def list_all_edges(self) -> List[Dict]:
        """Zwraca listę wszystkich krawędzi w grafie"""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                'from': u,
                'to': v,
                'type': data.get('type', 'unknown'),
                'length': data.get('length', 0.0),
                'bidirectional': data.get('bidirectional', True),
                'desc': data.get('desc', '')
            })
        return edges
    
    def get_edge_count_by_type(self) -> Dict[str, int]:
        """Zwraca liczbę krawędzi według typu"""
        counts = {}
        for _, row in self.edges_df.iterrows():
            edge_type = row.get('type', 'unknown')
            counts[edge_type] = counts.get(edge_type, 0) + 1
        return counts

    # --- Helpery klasyfikacji/holding ---
    def is_edge_holding_allowed(self, u: int, v: int) -> bool:
        """Czy na krawędzi (u,v) można oczekiwać (stać w kolejce)."""
        if self.graph.has_edge(u, v):
            return bool(self.graph[u][v].get('holding_allowed', False))
        return False

    def is_edge_type(self, u: int, v: int, t: str) -> bool:
        if self.graph.has_edge(u, v):
            return self.graph[u][v].get('type') == t
        return False
    
    def get_node_position(self, node_id: int) -> Optional[Tuple[int, int]]:
        """Pobiera pozycję węzła (x, y)"""
        node = self.get_node_by_id(node_id)
        if node:
            return (node['x'], node['y'])
        return None
    
    def get_neighbors(self, node_id: int) -> List[int]:
        """Pobiera sąsiadów węzła"""
        return list(self.graph.neighbors(node_id))
    
    def get_nodes_by_type(self, node_type: str) -> List[int]:
        """Pobiera wszystkie węzły określonego typu"""
        return [node_id for node_id, data in self.graph.nodes(data=True) 
                if data['type'] == node_type]
    
    def get_runway_nodes(self) -> List[int]:
        """Pobiera węzły pasów startowych"""
        return self.get_nodes_by_type('runway_thr')
    
    def get_stand_nodes(self) -> List[int]:
        """Pobiera węzły stanowisk postojowych"""
        return self.get_nodes_by_type('stand')
    
    def get_apron_nodes(self) -> List[int]:
        """Pobiera węzły płyt postojowych"""
        return self.get_nodes_by_type('apron')
    
    def get_taxiway_nodes(self) -> List[int]:
        """Pobiera węzły dróg kołowania"""
        return self.get_nodes_by_type('taxiway')
    
    def find_shortest_path(self, start: int, end: int) -> List[int]:
        """Znajduje najkrótszą ścieżkę między dwoma węzłami (respektuje jednokierunkowość)"""
        try:
            return nx.shortest_path(self.digraph, start, end, weight="length")
        except nx.NetworkXNoPath:
            return []
    
    def find_all_paths(self, start: int, end: int, max_length: int = 10) -> List[List[int]]:
        """Znajduje wszystkie ścieżki między dwoma węzłami (ograniczone długością), z kierunkami"""
        try:
            paths = list(nx.all_simple_paths(self.digraph, start, end, cutoff=max_length))
            # Sortuj według długości
            paths.sort(key=len)
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_edge_length(self, from_node: int, to_node: int) -> float:
        """Pobiera długość krawędzi między węzłami"""
        if self.graph.has_edge(from_node, to_node):
            return self.graph[from_node][to_node]['length']
        return 0.0
    
    def get_all_nodes(self) -> List[int]:
        """Pobiera wszystkie węzły"""
        return list(self.graph.nodes())
    
    def get_graph_bounds(self) -> Tuple[int, int, int, int]:
        """Pobiera granice grafu (min_x, max_x, min_y, max_y)"""
        x_coords = [data['x'] for _, data in self.graph.nodes(data=True)]
        y_coords = [data['y'] for _, data in self.graph.nodes(data=True)]
        
        return (min(x_coords), max(x_coords), min(y_coords), max(y_coords))
    
    def is_connected(self, node1: int, node2: int) -> bool:
        """Sprawdza czy węzły są połączone"""
        return self.graph.has_edge(node1, node2)
    
    def get_edge_type(self, from_node: int, to_node: int) -> Optional[str]:
        """Pobiera typ krawędzi między węzłami"""
        if self.graph.has_edge(from_node, to_node):
            return self.graph[from_node][to_node]['type']
        return None