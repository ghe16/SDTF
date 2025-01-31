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
            colors.append("blue")  
        elif cluster[node]["status"] == "inactive":
            colors.append("red")  
        elif cluster[node]["status"] == "responded":
            colors.append("cyan")  
        elif cluster[node]["status"] == "stale":
            colors.append("orange") 
        else:
            colors.append("green")  

    pos = nx.circular_layout(G)
    plt.clf()
    nx.draw(
        G, pos, with_labels=True, node_color=colors, node_size=700, font_weight="bold"
    )
    plt.title("Simulación de Disponibilidad en el Clúster")
    plt.pause(1)

# Simulación de replicación del mensaje
def replicate_message(leader, cluster):
    message = "Updated_by_leader"
    print(f"[Líder {leader}] Replicando mensaje: {message}")
    draw_cluster(leader, cluster)
    
    for node in NODES:
        if node != leader:
            is_stale = random.random() > 0.8  
            cluster[node]["data"] = message if not is_stale else "stale_data"
            print(f"[Nodo {node}] Datos actualizados a: {cluster[node]['data']}")
            
            # Simulación de petición externa mientras se actualiza
            target_node = random.choice(NODES)
            print(f"[Petición Externa] Enviada al Nodo {target_node}")
            if cluster[target_node]["data"] == "stale_data":
                print(f"[Nodo {target_node}] Responde con datos desactualizados")
                cluster[target_node]["status"] = "stale"
            else:
                print(f"[Nodo {target_node}] Responde con datos actualizados")
                cluster[target_node]["status"] = "responded"
    
    draw_cluster(leader, cluster)

# Visualización interactiva
plt.ion()
plt.figure(figsize=(8, 8))

for _ in range(5):
    CLUSTER = {node: {"data": "initial_value", "status": "active"} for node in NODES}
    LEADER = random.choice(NODES)  
    draw_cluster(LEADER, CLUSTER)
    time.sleep(7)
    replicate_message(LEADER, CLUSTER)
    time.sleep(7)

plt.ioff()
plt.show()
