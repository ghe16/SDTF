import random
import time

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.state = "follower"
        self.term = 0
        self.votes = 0
        self.log = []  # Lista de logs replicados

    def request_vote(self, nodes):
        """Simula la solicitud de votos para convertirse en líder."""
        self.state = "candidate"
        self.term += 1
        self.votes = 1  # Se vota a sí mismo
        print(f"Node {self.node_id} starts election for term {self.term}")

        #TODO

    def replicate_log(self, log_entry, nodes):
        """El líder envía el log a los seguidores."""
        if self.state == "leader":
            print(f"Leader {self.node_id} replicating log entry: {log_entry}")
            self.log.append(log_entry)

            for node in nodes:
                if node.node_id != self.node_id:
                    node.log.append(log_entry)
                    print(f"Node {node.node_id} replicated entry: {log_entry}")

    def print_logs(self):
        """Imprime el log del nodo."""
        print(f"Node {self.node_id} log: {self.log}")

def simulate_replicated_log():
    """Simula un sistema de replicación de logs en Raft."""
    nodes = [Node(i) for i in range(5)]

    # Se inicia una elección en un nodo aleatorio
    candidate = random.choice(nodes)
    candidate.request_vote(nodes)

    # Si hay un líder, replica un mensaje en el log
    leader = next((node for node in nodes if node.state == "leader"), None)
    if leader:
        leader.replicate_log("operation_1", nodes)

    # Mostrar los logs antes del fallo
    print("\nCurrent logs before leader failure:")
    for node in nodes:
        node.print_logs()

    # Simular fallo del líder y elección de un nuevo líder
    if leader:
        print(f"\nNode {leader.node_id} (leader) FAILS! A new election is triggered...\n")
        leader.state = "follower"
        time.sleep(1)

        # Un nuevo nodo inicia una elección
        new_candidate = random.choice([node for node in nodes if node.state != "leader"])
        new_candidate.request_vote(nodes)

        # Si el nuevo líder es elegido, replica una nueva operación: operation:_2
        #TODO

    # Mostrar logs después de la recuperación
    print("\nLogs after leader failure and recovery:")
    for node in nodes:
        node.print_logs()

simulate_replicated_log()
