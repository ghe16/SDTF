import random
import time

class RaftNode:
    def __init__(self, id, nodes):
        self.id = id
        self.nodes = nodes
        self.term = 0
        self.voted_for = None
        self.state = "Follower"
        self.votes_received = 0
        self.election_timeout = random.randint(3, 6)
        self.message_count = 0  # Track messages sent

    def start_election(self):
        """Starts a leader election and tracks time and messages exchanged."""
        start_time = time.time()  # Start timing
        self.term += 1
        self.state = "Candidate"
        self.voted_for = self.id
        self.votes_received = 1  

        print(f"🗳️ Node {self.id} starts election for Term {self.term}")
        for node in self.nodes:
            if node != self:
                self.message_count += 1  # Count vote request
                if node.vote(self.term, self.id):
                    self.votes_received += 1

        if self.votes_received > len(self.nodes) // 2:
            self.state = "Leader"
            elapsed_time = time.time() - start_time  # Calculate time taken
            print(f"🏆 Node {self.id} is elected Leader for Term {self.term}")
            print(f"⏳ Election Time: {elapsed_time:.4f} sec | 📩 Messages Sent: {self.message_count}")
        else:
            print(f"❌ Election failed, retrying...")
            time.sleep(self.election_timeout)
            self.start_election()

    def vote(self, term, candidate_id):
        """Handles vote requests and tracks messages."""
        self.message_count += 1  # Count vote response
        if term > self.term and self.voted_for is None:
            self.term = term
            self.voted_for = candidate_id
            print(f"✔️ Node {self.id} votes for {candidate_id} in Term {self.term}")
            return True
        return False

# Simulate Raft Leader Election
nodes = [RaftNode(i, None) for i in range(5)]
for node in nodes:
    node.nodes = nodes  

random.choice(nodes).start_election()
