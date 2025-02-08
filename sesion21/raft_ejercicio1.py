import matplotlib.pyplot as plt
import networkx as nx
import random
import time
import json

# Definir el número de nodos del clúster
NUM_NODES = 10
NODES = list(range(1, NUM_NODES + 1))
HEARTBEAT_INTERVAL = 2  # 
LOG_FILE = "raft_log.json"

# Crear la red gráfica
graph = nx.DiGraph()
graph.add_nodes_from(NODES)
pos = nx.circular_layout(graph) 

# Log del sistema
log = []

def save_log():
    with open(LOG_FILE, "w") as file:
        json.dump(log, file, indent=4)

def draw_cluster(leader=None, messages=[]):
    plt.clf()
    colors = []
    edge_labels = {}
    
    for node in NODES:
        if node == leader:
            colors.append("blue")  # 
        else:
            colors.append("orange")  
    
    graph.clear_edges()  
    edge_colors = []
    
    for node in NODES:
        for neighbor in NODES:
            if node != neighbor:
                graph.add_edge(node, neighbor)
                edge_colors.append("black")
    
    for sender, receiver, msg_type in messages:
        graph.add_edge(sender, receiver)
        edge_colors.append("red")  # Diferenciar los mensajes
        edge_labels[(sender, receiver)] = msg_type
    
    nx.draw(graph, pos, with_labels=True, node_color=colors, edge_color=edge_colors, node_size=700, font_weight="bold", arrows=True)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')
    plt.title("Simulación de Elección de Líder en Raft")
    plt.pause(1)

# Elección de líder en Raft
def elect_leader(candidates):
    #TODO
    # create random timeouts for each node in a dictionary de nombre timeouts = {node:timeout"}
    
    # ordenar los candidatos, del tiempo más bajo al más alto ponerlo en una variable de nombre sorted_candidates
    
    # crear un diccionario llamado votes. votes contendrá la votación inicial... (cada nodo se vota a si mismo). El diccionario tendra la forma votes = {node: 1}
    
    
    voted_nodes = set()
    messages = []
    
    for candidate in sorted_candidates:
        print(f"[Nodo {candidate}] Se postula como líder tras {timeouts[candidate]:.2f} segundos.")
        for voter in candidates:
            if voter != candidate and voter not in voted_nodes:
                if random.random() < 0.5:
                    print(f"[Nodo {voter}] Vota por {candidate}")
                    # TODO: 
                    # incrementar los votos de ese candidato  (variable votes)
                    
                    # anyadir ese voto a la lista para saber cual es el más votado. (variable voted_nodes)

                    messages.append((voter, candidate, "Voto"))
    
    draw_cluster(messages=messages)
    
    max_votes = max(votes.values(), default=0)
    winners = [node for node, v in votes.items() if v == max_votes]
    
    if len(winners) == 1:
        print(f"Nuevo líder elegido: Nodo {winners[0]}")
        return winners[0]
    else:
        print("Empate en la elección, reiniciando proceso...")
        return elect_leader(candidates)

# Simulación del envío de heartbeats
def send_heartbeats(leader):
    messages = []
    print(f"[Líder {leader}] Enviando heartbeats...")
    for node in NODES:
        if node != leader:
            print(f"[Nodo {node}] Recibió heartbeat de {leader}")
            messages.append((leader, node, "Heartbeat"))
    draw_cluster(leader=leader, messages=messages)
    time.sleep(HEARTBEAT_INTERVAL)

# Simulación del envío de append entries
def append_entries(leader):
    global log
    term = len(log) + 1
    operation = f"Operación {term}"
    log.append({"term": term, "operation": operation})
    save_log()
    messages = []
    print(f"[Líder {leader}] Enviando AppendEntries: {operation}")
    for node in NODES:
        if node != leader:
            print(f"[Nodo {node}] Aplica {operation}")
            messages.append((leader, node, "AppendEntries"))
    draw_cluster(leader=leader, messages=messages)
    time.sleep(HEARTBEAT_INTERVAL)

# Simulación principal
plt.ion()
plt.figure(figsize=(8, 8))

print("### Elección de líder ###")
LEADER = elect_leader(NODES)
draw_cluster(LEADER)

for i in range(1,6):
    send_heartbeats(LEADER)
    send_heartbeats(LEADER)
    append_entries(LEADER)
    time.sleep(HEARTBEAT_INTERVAL)

plt.ioff()
plt.show()
