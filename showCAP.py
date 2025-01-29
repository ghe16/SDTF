from time import sleep
import random

data_store_node1 = {"key": "initial_value"}
data_store_node2 = {"key": "initial_value"}

def simulate_write(node, value):
    print(f"[Nodo {node}] Escribiendo valor: {value}")
    if node == 1:
        data_store_node1["key"] = value
    else:
        data_store_node2["key"] = value

def simulate_read(node):
    print(f"[Nodo {node}] Leyendo valor...")
    if node == 1:
        return data_store_node1["key"]
    else:
        return data_store_node2["key"]

def simulate_partition():
    return random.choice([True, False])  # Simula una partición con un 50% de probabilidad

# Simulación
simulate_write(1, "updated_by_node1")

if simulate_partition():
    print("** Partición de red detectada **")
    print(f"[Nodo 2] Valor disponible localmente: {simulate_read(2)}")
else:
    print(f"[Nodo 2] Leyendo desde Nodo 1: {simulate_read(1)}")
