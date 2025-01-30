from time import sleep

data_store = {"key": "initial_value"}  # Base de datos compartida por dos nodos

def update_node1():
    data_store["key"] = "updated_by_node1"
    print("[Nodo 1] Valor actualizado a:", data_store["key"])

def read_node2():
    print("[Nodo 2] Valor leído:", data_store["key"])

# Nodo 1 actualiza, Nodo 2 lee inmediatamente
update_node1()
read_node2()