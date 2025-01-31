data_store_node1 = {"key": "initial_value"}
data_store_node2 = {"key": "initial_value"}

def update_node1():
    print("[Nodo 1] Actualizando valor...")
    data_store_node1["key"] = "updated_by_node1"

def read_node2():
    print("[Nodo 2] Intentando leer valor...")
    try:
        # Simulación: Nodo 2 no puede comunicarse con Nodo 1
        raise ConnectionError("Fallo en la red")
    except ConnectionError as e:
        print("[Nodo 2] No se puede acceder al nodo 1:", e)

# Simulación de una partición de red
update_node1()
read_node2()
