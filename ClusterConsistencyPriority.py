import matplotlib.pyplot as plt
import networkx as nx
import random
import time

# Definir el número de nodos del clúster
NUM_NODES = 10  # Se puede cambiar este valor
NODES = list(range(1, NUM_NODES + 1))

# Crear la red gráfica
G = nx.Graph()
G.add_nodes_from(NODES)
for i in NODES:
    for j in NODES:
        if i != j:
            G.add_edge(i, j)

# Función para mostrar el clúster
def draw_cluster(leader, cluster):
    colors = []
    for node in NODES:
        if node == leader:
            colors.append("blue")  # Nodo líder en azul
        elif cluster[node]["status"] == "inactive":
            colors.append("red")  # Nodos inactivos en rojo
        elif cluster[node]["status"] == "rejected":
            colors.append("pink")  # Nodos que rechazaron la actualización en rosa
        elif cluster[node]["status"] == "accepted":
            colors.append("cyan")  # Nodos que aceptaron una petición externa en celeste
        else:
            colors.append("green")  # Nodos activos en verde

    pos = nx.circular_layout(G)
    plt.clf()
    nx.draw(
        G, pos, with_labels=True, node_color=colors, node_size=700, font_weight="bold"
    )
    plt.title("Simulación de Consistencia en el Clúster")
    plt.pause(1)

# Simulación de replicación del mensaje
def replicate_message(leader, cluster):
    message = "Updated_by_leader"
    print(f"[Líder {leader}] Replicando mensaje: {message}")
    draw_cluster(leader, cluster)
    
    num_rejected = random.randint(0, len(NODES) - 1)
    rejected_nodes = random.sample([node for node in NODES if node != leader], num_rejected)
    
    for node in NODES:
        if node != leader:
            # Simulación de petición externa mientras se actualiza
            target_node = random.choice(NODES)
            print(f"[Petición Externa] Enviada al Nodo {target_node}")
            if cluster[target_node]["data"] == "Updated_by_leader":
                print(f"[Nodo {target_node}] Acepta la petición externa")
                cluster[target_node]["status"] = "accepted"
            else:
                print(f"[Nodo {target_node}] Rechaza la petición externa (datos desactualizados)")
                cluster[target_node]["status"] = "rejected"

            if node in rejected_nodes:
                print(f"[Nodo {node}] Rechaza la actualización para garantizar consistencia")
                cluster[node]["status"] = "rejected"
            else:
                cluster[node]["data"] = message
                print(f"[Nodo {node}] Datos actualizados correctamente.")
            #TODO: crear variables para recuperar los datos de nodos que rechazan peticiones (REJECTED), y  peticiones aceptadas (CORRECTAS) y peticiones aceptadas (INCORRECTAS)  
    
    draw_cluster(leader, cluster)

# Visualización interactiva
plt.ion()
plt.figure(figsize=(8, 8))

for _ in range(5):
    CLUSTER = {node: {"data": "initial_value", "status": "active"} for node in NODES}
    LEADER = random.choice(NODES)  # Elegir un líder diferente en cada iteración
    draw_cluster(LEADER, CLUSTER)
    time.sleep(2)
    replicate_message(LEADER, CLUSTER)
    time.sleep(2)

plt.ioff()
plt.show()