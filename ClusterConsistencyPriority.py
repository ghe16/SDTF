import matplotlib
matplotlib.use('TkAgg')  # O 'Agg' si no necesitas interfaz gráfica
import matplotlib.pyplot
import networkx as nx
import random
import time


# Definir los nodos del clúster
NODES = [1, 2, 3, 4, 5]
CLUSTER = {node: {"data": "initial_value", "status": "active"} for node in NODES}
LEADER = 1  # Nodo líder

# Crear la red gráfica
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
        if node == LEADER:
            colors.append("blue")  # Nodo líder en azul
        elif CLUSTER[node]["status"] == "active":
            colors.append("green")  # Nodos activos en verde
        else:
            colors.append("red")  # Nodos inactivos en rojo

    pos = nx.circular_layout(G)
    matplotlib.pyplot.plt.clf()
    nx.draw(
        G, pos, with_labels=True, node_color=colors, node_size=700, font_weight="bold"
    )
    plt.title("Simulación de Consistencia en el Clúster")
    plt.pause(1)

# Simulación de replicación del mensaje
def replicate_message():
    message = "Updated_by_leader"
    print(f"[Líder {LEADER}] Replicando mensaje: {message}")
    draw_cluster()
    
    for node in NODES:
        if node != LEADER:
            if node == random.choice(NODES[1:]):  # Un nodo rechaza la actualización
                print(f"[Nodo {node}] Rechaza la actualización para garantizar consistencia")
            else:
                CLUSTER[node]["data"] = message
                print(f"[Nodo {node}] Datos actualizados correctamente.")
    
    draw_cluster()

# Visualización interactiva
plt.ion()
plt.figure(figsize=(8, 8))
draw_cluster()
time.sleep(2)
replicate_message()
plt.ioff()
plt.show()
