import networkx as nx
import matplotlib.pyplot as plt
import random
import time

class PaxosVisualizer:
    """ Manages the graphical representation of Paxos messages. """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.pos = {}
        self.step = 0
        self.logs = []
        self.fig, self.ax = plt.subplots()
        
    def log_event(self, sender, receiver, message):
        """ Logs an event and updates the graph. """
        self.logs.append(f"Step {self.step}: {sender} → {receiver}: {message}")
        self.graph.remove_edges_from(list(self.graph.edges(sender)))  # Remove previous edges from sender
        self.graph.add_edge(sender, receiver, label=message)
        self.step += 1
        self.draw_graph()
        time.sleep(1)  # Simulating delay for better visualization
    
    def draw_graph(self):
        """ Draws the current state of the Paxos network. """
        self.ax.clear()
        labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw(self.graph, self.pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, ax=self.ax)
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=labels, font_color='red', ax=self.ax)
        plt.pause(0.5)

    def initialize_graph(self, num_acceptors):
        """ Initializes the nodes and their positions in the visualization. """
        self.graph.add_node("Proposer")
        self.pos["Proposer"] = (0, 0)
        for i in range(num_acceptors):
            acceptor_name = f"Acceptor {i}"
            self.graph.add_node(acceptor_name)
            self.pos[acceptor_name] = (i - num_acceptors // 2, -1)
        self.graph.add_node("Learner")
        self.pos["Learner"] = (0, -2)
        self.draw_graph()
    
    def get_logs(self):
        """ Returns logged messages as text output. """
        return "\n".join(self.logs)

class Acceptor:
    def __init__(self, id, visualizer):
        self.id = id
        self.promised_id = None
        self.accepted_id = None
        self.accepted_value = None
        self.visualizer = visualizer

    def prepare(self, proposal_id):
        """ Handles the Prepare phase. """
        if self.promised_id is None or proposal_id > self.promised_id:
            self.promised_id = proposal_id
            self.visualizer.log_event(f"Acceptor {self.id}", "Proposer", f"Promise {proposal_id}")
            return True, self.accepted_id, self.accepted_value
        self.visualizer.log_event(f"Acceptor {self.id}", "Proposer", f"Reject {proposal_id}")
        return False, self.accepted_id, self.accepted_value

    def accept(self, proposal_id, value):
        """ Handles the Accept phase. """
        if proposal_id >= self.promised_id:
            self.accepted_id = proposal_id
            self.accepted_value = value
            self.visualizer.log_event(f"Acceptor {self.id}", "Proposer", f"Accept {proposal_id}, {value}")
            return True
        return False

class Proposer:
    def __init__(self, id, acceptors, visualizer):
        self.id = id
        self.acceptors = acceptors
        self.proposal_id = random.randint(1, 100)
        self.visualizer = visualizer

    def propose(self, value):
        """ Executes Paxos rounds. """
        for acceptor in self.acceptors:
            self.visualizer.log_event("Proposer", f"Acceptor {acceptor.id}", f"Propose {value} with ID {self.proposal_id}")
        
        promises = []
        
        for acceptor in self.acceptors:
            success, _, _ = acceptor.prepare(self.proposal_id)
            if success:
                promises.append(acceptor)

        if len(promises) < len(self.acceptors) // 2 + 1:
            for acceptor in self.acceptors:
                self.visualizer.log_event("Proposer", f"Acceptor {acceptor.id}", f"Proposal {self.proposal_id} rejected")
            return None  
        
        accepted_count = 0
        for acceptor in promises:
            if acceptor.accept(self.proposal_id, value):
                accepted_count += 1

        if accepted_count >= len(self.acceptors) // 2 + 1:
            for acceptor in promises:
                self.visualizer.log_event(f"Acceptor {acceptor.id}", "Learner", f"Consensus Reached: {value}")
            return value
        else:
            for acceptor in promises:
                self.visualizer.log_event("Proposer", f"Acceptor {acceptor.id}", f"Proposal {self.proposal_id} failed")
            return None

class Learner:
    def __init__(self, visualizer):
        self.final_value = None
        self.visualizer = visualizer

    def learn(self, value):
        """ Stores the final agreed-upon value. """
        self.final_value = value
        for acceptor in range(NUM_ACCEPTORS):
            self.visualizer.log_event("Learner", f"Acceptor {acceptor}", f"Final Decision: {value}")
        self.visualizer.log_event("Learner", "Proposer", f"Final Decision: {value}")

# Set the number of acceptors
NUM_ACCEPTORS = 5

# Initialize the visualizer
visualizer = PaxosVisualizer()
visualizer.initialize_graph(NUM_ACCEPTORS)

# Simulate Paxos
acceptors = [Acceptor(i, visualizer) for i in range(NUM_ACCEPTORS)]
proposer = Proposer(1, acceptors, visualizer)
learner = Learner(visualizer)

# Run Paxos Consensus
final_value = proposer.propose("X=10")
if final_value:
    learner.learn(final_value)

# Output logs for debugging
print(visualizer.get_logs())
plt.show()
