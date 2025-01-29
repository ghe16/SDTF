import matplotlib.pyplot as plt
import networkx as nx
import random
import time

# Crear un clúster simulado con 5 nodos
NODES = [1, 2, 3, 4, 5]
CLUSTER = {node: {"data": "initial_value", "status": "active"} for node in NODES}

# Configurar la red gráfica
G = nx.Graph()
G.add_nodes_from(NODES)
for i in NODES:
    for j in NODES:
        if i != j:
            G.add_edge(i, j)

# Función para mostrar el clúster
def draw_cluster():
    colors = []
    for node in NODES:
        if CLUSTER[node]["status"] == "active":
            colors.append("green")
        else:
            colors.append("red")

    pos = nx.circular_layout(G)
    nx.draw(
        G, pos, with_labels=True, node_color=colors, node_size=700, font_weight="bold"
    )
    plt.pause(1)

# Simulación de operaciones en el clúster
def simulate_operation():
    active_nodes = [node for node in NODES if CLUSTER[node]["status"] == "active"]
    if not active_nodes:
        print("No hay nodos activos. El sistema no está disponible.")
        return
    # Nodo elegido para escritura
    leader = random.choice(active_nodes)
    new_value = f"updated_by_node_{leader}"
    print(f"[Nodo {leader}] Actualizando valor a: {new_value}")
    for node in active_nodes:
        CLUSTER[node]["data"] = new_value
    print(f"Todos los nodos activos tienen el valor: {new_value}")

# Simular particiones de red
def simulate_partition():
    node = random.choice(NODES)
    CLUSTER[node]["status"] = "inactive"
    print(f"** Nodo {node} desconectado (Partición de red) **")

# Restaurar nodos
def restore_node():
    node = random.choice(NODES)
    if CLUSTER[node]["status"] == "inactive":
        CLUSTER[node]["status"] = "active"
        print(f"** Nodo {node} restaurado **")

# Visualización interactiva
plt.ion()
plt.figure(figsize=(8, 8))
plt.title("Simulación del Clúster Distribuido (CAP)")
for _ in range(10):
    draw_cluster()
    action = random.choice(["write", "partition", "restore"])
    if action == "write":
        simulate_operation()
    elif action == "partition":
        simulate_partition()
    elif action == "restore":
        restore_node()
    time.sleep(2)

plt.ioff()
plt.show()
