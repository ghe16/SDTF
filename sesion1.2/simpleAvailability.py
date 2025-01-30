data_store_node1 = {"key": "initial_value"}
data_store_node2 = {"key": "initial_value"}

def update_node1():
    data_store_node1["key"] = "updated_by_node1"
    print("[Nodo 1] Valor actualizado a:", data_store_node1["key"])

def read_node2():
    print("[Nodo 2] Valor leído:", data_store_node2["key"])

# Simulación: Nodo 1 actualiza, Nodo 2 responde con datos desactualizados
update_node1()
read_node2()
