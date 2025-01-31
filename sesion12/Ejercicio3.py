import matplotlib.pyplot as plt
import networkx as nx
import random
import time

# Definir el número de nodos del clúster
NUM_NODES = 10  # Se puede cambiar este valor
NODES = list(range(1, NUM_NODES + 1))

# Generar posiciones fijas para los nodos
pos = nx.spring_layout(nx.complete_graph(NODES), seed=42)  # Semilla fija para mantener la disposición

# Función para simular una única partición de red en dos grupos
def simulate_partition():
    shuffled_nodes = random.sample(NODES, len(NODES))  # Mezclar nodos aleatoriamente
    split_index = len(shuffled_nodes) // 2  # Dividir en dos grupos
    partition1 = set(shuffled_nodes[:split_index])
    partition2 = set(shuffled_nodes[split_index:])
    
    # Asegurar que los conjuntos sean disjuntos
    assert partition1.isdisjoint(partition2), "Error: Un nodo pertenece a ambas particiones"
    
    partitioned_clusters = [partition1, partition2]
    print(f"** Partición de red: {partitioned_clusters} **")
    
    return partitioned_clusters

# Función para construir un nuevo grafo sin enlaces entre particiones
def build_partitioned_graph(partitions):
    new_G = nx.Graph()
    new_G.add_nodes_from(NODES)
    for partition in partitions:
        for u in partition:
            for v in partition:
                if u != v:
                    new_G.add_edge(u, v)
    return new_G

# Función para mostrar el clúster
def draw_cluster(leader_map, partitions, cluster, graph):
    colors = []
    edge_colors = []
    
    partition_colors = ["yellow", "blue"]  # Colores distintos para cada partición
    partition_map = {node: idx for idx, partition in enumerate(partitions) for node in partition}
    
    for node in NODES:
        if node not in cluster or cluster[node]["status"] == "inactive":
            colors.append("red")  # Nodo inactivo en rojo
        elif any(node in p for p in partitions):
            leader = leader_map.get(node, None)
            if node == leader:
                colors.append("blue")  # Nodo líder en azul
            elif cluster[node]["status"] == "replicated":
                colors.append("orange")  # Nodo que replicó en naranja
            elif cluster[node]["status"] == "updated":
                colors.append("green")  # Nodo actualizado a verde
            elif cluster[node]["status"] == "cyan":
                colors.append("cyan")  # Nodo actualizado por petición externa
            elif cluster[node]["status"] == "stale_data":
                colors.append("orange")  # Nodo con datos desactualizados en naranja
            elif cluster[node]["status"] == "stale_request":
                colors.append("purple")  # Nodo que recibió una petición externa con datos desactualizados en morado
            else:
                colors.append("green")  # Nodo activo en verde
        else:
            colors.append("red")  # Nodo aislado
    
    for edge in graph.edges():
        if edge[0] in partition_map and edge[1] in partition_map and partition_map[edge[0]] == partition_map[edge[1]]:
            edge_colors.append(partition_colors[partition_map[edge[0]]])  # Color basado en la partición
        else:
            edge_colors.append("black")  # Enlaces generales en negro
    
    plt.clf()
    nx.draw(graph, pos, with_labels=True, node_color=colors, node_size=700, font_weight="bold", edge_color=edge_colors)
    plt.title("Simulación de Disponibilidad con Particiones de Red")
    plt.pause(1)

# Simulación de replicación de mensajes
def replicate_message(leader_map, cluster, partitions, graph):
    for partition in partitions:
        if not partition:
            continue
        leader = leader_map.get(min(partition), None)
        if leader is None:
            leader = min(partition)
            leader_map[leader] = leader  # Asignar un nuevo líder si no está presente
        
        message = f"Updated_by_leader_{leader}"
        print(f"[Líder {leader}] Replicando mensaje en su partición: {message}")
        
        for node in partition:
            if node != leader:
                is_stale = random.random() > 0.1  # 20% de probabilidad de datos desactualizados
                cluster[node]["data"] = message if not is_stale else "stale_data"
                cluster[node]["status"] = "updated" if not is_stale else "stale_data"
                print(f"[Nodo {node}] Datos actualizados a: {cluster[node]['data']}")
                
        # Simular petición externa
        target_node = random.choice(list(partition))
        if target_node == leader:
            cluster[target_node]["status"] = "cyan"
            print(f"[Líder {target_node}] Recibió petición externa - Siempre datos actualizados")
        elif cluster[target_node]["data"] == "stale_data":
            cluster[target_node]["status"] = "stale_request"
            print(f"[Nodo {target_node}] Recibió petición externa - Datos desactualizados (morado)")
        else:
            cluster[target_node]["status"] = "cyan"
            print(f"[Nodo {target_node}] Recibió petición externa - Datos actualizados")
        
        draw_cluster(leader_map, partitions, cluster, graph)
        time.sleep(1)

# Visualización interactiva
plt.ion()
plt.figure(figsize=(8, 8))

# Estado inicial con todos los nodos conectados
INITIAL_LEADER = random.choice(NODES)
CLUSTER = {node: {"data": "initial_value", "status": "active"} for node in NODES}
leader_map = {INITIAL_LEADER: INITIAL_LEADER}
G = nx.complete_graph(NODES)
draw_cluster(leader_map, [], CLUSTER, G)
time.sleep(2)

# Primera replicación antes de la partición
replicate_message(leader_map, CLUSTER, [set(NODES)], G)
time.sleep(2)

# Realizar una única partición
partitions = simulate_partition()
new_G = build_partitioned_graph(partitions)
leader_map = {min(partition): min(partition) for partition in partitions if partition}  # Asegurar que cada partición tenga líder
draw_cluster(leader_map, partitions, CLUSTER, new_G)
time.sleep(2)

# Replicar mensaje después de la partición
replicate_message(leader_map, CLUSTER, partitions, new_G)
time.sleep(2)

plt.ioff()
plt.show()
