import random
import time
import threading

class Acceptor:
    def __init__(self, id):
        self.id = id
        self.promised_id = None  # Highest Proposal ID promised
        self.accepted_id = None  # Highest Proposal ID accepted
        self.accepted_value = None

    def prepare(self, proposal_id):
        """Handles a prepare request from a Proposer."""
        time.sleep(random.uniform(0.1, 0.5))  # Simulate network delay

        if self.promised_id is None or proposal_id > self.promised_id:
            self.promised_id = proposal_id
            print(f"✅ Acceptor {self.id} promises Proposal {proposal_id}")
            return True, self.accepted_id, self.accepted_value
        print(f"❌ Acceptor {self.id} rejects Proposal {proposal_id} (Already Promised {self.promised_id})")
        return False, self.accepted_id, self.accepted_value

    def accept(self, proposal_id, value):
        """Handles an accept request from a Proposer."""
        if proposal_id >= self.promised_id:
            self.accepted_id = proposal_id
            self.accepted_value = value
            print(f"🎯 Acceptor {self.id} accepts Proposal {proposal_id} with Value: {value}")
            return True
        print(f"❌ Acceptor {self.id} rejects Proposal {proposal_id} (Lower than {self.promised_id})")
        return False

class Proposer:
    def __init__(self, id, acceptors):
        self.id = id
        self.acceptors = acceptors
        self.proposal_id = random.randint(1, 100)  # Ensure Proposers have different IDs
        self.message_count = 0  

    def propose(self, value):
        """Runs a full Paxos round, ensuring conflicts occur."""
        print(f"\n🚀 Proposer {self.id} starts with Proposal ID {self.proposal_id}")
        time.sleep(random.uniform(0.1, 0.5))  # Introduce randomness to proposer start time
        promises = 0
        accepted_count = 0

        # Step 1: Send Prepare Requests
        for acceptor in self.acceptors:
            success, _, _ = acceptor.prepare(self.proposal_id)
            if success:
                promises += 1

        # If not enough promises, retry with a higher proposal ID
        if promises < len(self.acceptors) // 2 + 1:
            print(f"❌ Proposer {self.id} failed to get a majority. Retrying with higher ID...")
            self.proposal_id = max([p.proposal_id for p in proposers]) + random.randint(1, 10)  # Ensure next ID is higher
            time.sleep(1)
            return self.propose(value)

        # Step 2: Send Accept Requests
        for acceptor in self.acceptors:
            if acceptor.accept(self.proposal_id, value):
                accepted_count += 1

        # If accepted by a majority, consensus is reached
        if accepted_count >= len(self.acceptors) // 2 + 1:
            print(f"🏆 Proposer {self.id} wins consensus with Value: {value} (Proposal {self.proposal_id})")
        else:
            print(f"⚠️ Proposer {self.id} lost consensus. Retrying with a new ID...")
            self.proposal_id = max([p.proposal_id for p in proposers]) + random.randint(1, 10)
            time.sleep(1)
            return self.propose(value)

# Run with multiple competing Proposers
acceptors = [Acceptor(i) for i in range(5)]
proposers = [Proposer(i, acceptors) for i in range(3)]  # Three competing Proposers

# Run Proposers in parallel to introduce conflicts
threads = [threading.Thread(target=p.propose, args=(f"Value-{p.id}",)) for p in proposers]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
