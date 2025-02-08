import networkx as nx
import matplotlib.pyplot as plt
import random
import time

# Configuración inicial
NODES = ['Leader', 'Follower1', 'Follower2', 'Follower3']
leader = 'Leader'
followers = NODES[1:]

# Estructuras de datos para almacenar los logs de cada nodo
logs = {node: [] for node in NODES}

# Función para generar operaciones simuladas
def generate_operation(index):
    return {'index': index, 'operation': f'Op{index}', 'timestamp': time.time()}

# Función para visualizar el estado de los logs
def visualize_logs():
    plt.clf()
    plt.figure(figsize=(8, 6))
    G = nx.DiGraph()
    G.add_nodes_from(NODES)
    pos = nx.spring_layout(G, seed=42)
    
    for node in NODES:
        log_entries = [entry['operation'] for entry in logs[node]]
        nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='lightblue', node_size=3000)
        nx.draw_networkx_labels(G, pos, labels={node: f"{node}\n{log_entries}"})
    
    nx.draw_networkx_edges(G, pos, edgelist=[(leader, f) for f in followers], arrowstyle='->')
    plt.title("Estado de los logs en los nodos")
    plt.pause(0.5)  # Pequeña pausa para visualizar cambios

# Simulación de replicación inicial de logs
def initial_log_replication():
    for i in range(1, 11):
        operation = generate_operation(i)
        logs[leader].append(operation)
        print(f"{leader} generó {operation['operation']}")
        
        for follower in followers:
            if random.random() > 0.2:  # 80% de probabilidad de aceptar la entrada
                logs[follower].append(operation)
                print(f"{follower} aceptó {operation['operation']}")
            else:
                print(f"{follower} rechazó {operation['operation']}")
        
        visualize_logs()

# Proceso de sincronización de logs
def synchronize_logs():
    for follower in followers:
        leader_log = logs[leader]
        follower_log = logs[follower]
        
        # Buscar la última posición coincidente desde el final
        mismatch_index = -1
        for i in range(min(len(leader_log), len(follower_log)) - 1, -1, -1):
            if follower_log[i]['operation'] != leader_log[i]['operation']:
                mismatch_index = i
            
        # Si hay discrepancia, actualizar desde el punto donde difiere hasta el final
        if mismatch_index != -1:
            follower_log[mismatch_index:] = leader_log[mismatch_index:]
            print(f"{follower} sincronizó desde {leader_log[mismatch_index]['operation']} en adelante")
        
        visualize_logs()

# Ejecutar la simulación
plt.ion()  # Activar modo interactivo
initial_log_replication()
print("Estado inicial de los logs:")
for node, log in logs.items():
    print(f"{node}: {[entry['operation'] for entry in log]}")
visualize_logs()

synchronize_logs()
print("\nDespués de la sincronización:")
for node, log in logs.items():
    print(f"{node}: {[entry['operation'] for entry in log]}")
visualize_logs()
plt.ioff()  # Desactivar modo interactivo
plt.show()
