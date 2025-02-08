import matplotlib.pyplot as plt
import networkx as nx
import random
import time
import threading

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

# Simulación de partición de red
def simulate_partition():
    partition_size = NUM_NODES // 2
    cluster1 = set(random.sample(NODES, partition_size))
    cluster2 = set(NODES) - cluster1
    print(f"** Partición de red: Cluster 1 {cluster1}, Cluster 2 {cluster2} **")
    
    # Eliminar todas las conexiones
    G.clear_edges()
    
    # Agregar conexiones internas en cada cluster
    for node in cluster1:
        for neighbor in cluster1:
            if node != neighbor:
                G.add_edge(node, neighbor)
    
    for node in cluster2:
        for neighbor in cluster2:
            if node != neighbor:
                G.add_edge(node, neighbor)
    
    return cluster1, cluster2

# Función para mostrar el clúster
def draw_cluster(leader1, leader2, cluster1=set(), cluster2=set()):
    colors = []
    edge_colors = []
    for node in NODES:
        if node == leader1:
            colors.append("blue")  
        elif node == leader2:
            colors.append("purple")  
        elif node in cluster1:
            colors.append("green")  
        elif node in cluster2:
            colors.append("yellow")  
        else:
            colors.append("red")  # 

    pos = nx.circular_layout(G)
    plt.clf()
    edges = G.edges()
    for edge in edges:
        if edge[0] in cluster1 and edge[1] in cluster1:
            edge_colors.append("black")  # Enlaces internos del primer clúster
        elif edge[0] in cluster2 and edge[1] in cluster2:
            edge_colors.append("yellow")  # Enlaces internos del segundo clúster

    nx.draw(
        G, pos, with_labels=True, node_color=colors, edge_color=edge_colors, node_size=700, font_weight="bold"
    )
    plt.title("Simulación de Elección de Líder en Raft")
    plt.pause(1)

# Simulación del envío de heartbeats
def send_heartbeats(leader, cluster):
    print(f"[Líder {leader}] Enviando heartbeats a todos los nodos...")
    for node in cluster:
        if node != leader:
            print(f"[Nodo {node}] Recibió heartbeat del líder {leader}")

# Elección de líder en Raft con simulación de split vote
def elect_leader(candidates, force_tie=False):
    round_count = 0
    split_vote_occurred = False
    
    while True:
        round_count += 1
        if force_tie:
            timeouts = {node: 3.0 for node in candidates}  # Fuerza empate en la primera ronda
            force_tie = False  # Solo ocurre en la primera iteración
        else:
            timeouts = {node: random.uniform(1, 5) for node in candidates}
        print(f"Ronda {round_count} - Tiempos de espera para ser candidato: {timeouts}")
        
        # Verificar si todos los nodos tienen el mismo timeout
        if len(set(timeouts.values())) == 1:
            print("Empate en los timeouts, generando nuevos valores...")
            continue
        
        votes = {node: 0 for node in candidates}  # Inicializar los votos en 0
        vote_record = {node: [] for node in candidates}  # Registro de votos recibidos
        voted_nodes = set()
        election_lock = threading.Lock()

        def candidate_wait(node, timeout):
            time.sleep(timeout)
            with election_lock:
                print(f"[Nodo {node}] Se postula como líder después de {timeout:.2f} segundos.")
                for voter in candidates:
                    if voter != node and voter not in voted_nodes:
                        if random.random() < 0.5:  # Probabilidad de generar un split vote
                            print(f"[Nodo {voter}] Vota por {node}")
                                                # TODO: 
                            # incrementar los votos de ese nodo candidato  (variable votes)
                            
                            # anyadir ese voto a la lista para saber cual es el más votado. (variable voted_nodes)

                            vote_record[node].append(voter)
                        else:
                            print(f"[Nodo {voter}] Rechaza a {node} porque ya ha votado.")

        threads = []
        for node, timeout in timeouts.items():
            thread = threading.Thread(target=candidate_wait, args=(node, timeout))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        
        max_votes = max(votes.values(), default=0)
        winners = [node for node, v in votes.items() if v == max_votes]
        
        if len(winners) == 1:
            print(f"Nuevo líder elegido en la ronda {round_count}: Nodo {winners[0]} con {max_votes} votos de {vote_record[winners[0]]}")
            return winners[0]
        else:
            split_vote_occurred = True
            print(f"Ronda {round_count} - Split vote detectado, asignando nuevos tiempos de espera y repitiendo proceso...")

# Visualización interactiva
plt.ion()
plt.figure(figsize=(8, 8))

print("### Elección de líder inicial ###")
LEADER = elect_leader(NODES, force_tie=True)  # Fuerza un empate en la primera elección
draw_cluster(LEADER, None, cluster1=NODES)

time.sleep(2)
send_heartbeats(LEADER, NODES)
time.sleep(2)

print("### Simulación de partición de red ###")
cluster1, cluster2 = simulate_partition()
draw_cluster(None, None, cluster1=cluster1, cluster2=cluster2)
time.sleep(2)

print("### Nueva elección de líderes tras la partición ###")
leader1 = elect_leader(cluster1)
leader2 = elect_leader(cluster2)
draw_cluster(leader1, leader2, cluster1=cluster1, cluster2=cluster2)
time.sleep(2)

plt.ioff()
plt.show()
