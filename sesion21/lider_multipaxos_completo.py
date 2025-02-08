import random
import time

class Acceptor:
    def __init__(self, id):
        self.id = id
        self.highest_term_seen = 0
        self.promised_term = None
        self.message_count = 0  

    def receive_prepare(self, proposer_term, proposer_id):
        """Handles a Prepare message and tracks messages exchanged."""
        self.message_count += 1  # Count received Prepare message
        if proposer_term > self.highest_term_seen:
            self.highest_term_seen = proposer_term
            self.promised_term = proposer_term
            print(f"✅ Acceptor {self.id} promises to Proposer {proposer_id} (Term {proposer_term})")
            return True
        print(f"❌ Acceptor {self.id} rejects Proposer {proposer_id} (Term {proposer_term})")
        return False

class Proposer:
    def __init__(self, id, acceptors):
        self.id = id
        self.acceptors = acceptors
        self.term = random.randint(1, 100)
        self.message_count = 0  

    def start_election(self):
        """Starts a Multi-Paxos election, tracking time and messages."""
        start_time = time.time()
        votes = 0
        print(f"📢 Proposer {self.id} starts leader election with Term {self.term}")

        for acceptor in self.acceptors:
            self.message_count += 1  # Count Prepare messages
            if acceptor.receive_prepare(self.term, self.id):
                votes += 1

        if votes > len(self.acceptors) // 2:
            elapsed_time = time.time() - start_time  
            print(f"🏆 Proposer {self.id} is elected as Leader in Term {self.term}")
            print(f"⏳ Election Time: {elapsed_time:.4f} sec | 📩 Messages Sent: {self.message_count}")
        else:
            print(f"❌ Election failed, retrying...")
            time.sleep(2)
            self.term += 1
            self.start_election()

# Simulate Multi-Paxos Leader Election
acceptors = [Acceptor(i) for i in range(5)]
proposer = Proposer(1, acceptors)
proposer.start_election()
