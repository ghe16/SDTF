import random

class Acceptor:
    def __init__(self, id):
        """
        Initialize an Acceptor.
        :param id: Unique identifier for the Acceptor.
        """
        self.id = id
        self.promised_id = None
        self.accepted_id = None
        self.accepted_value = None  

    def prepare(self, proposal_id):
        """
        Handles the Prepare phase.
        :param proposal_id: Proposal ID sent by the Proposer.
        :return: Promise response.
        """
        if self.promised_id is None or proposal_id > self.promised_id:
            self.promised_id = proposal_id
            print(f"✅ Acceptor {self.id} PROMISES Proposal {proposal_id}")
            return True, self.accepted_id, self.accepted_value
        
        print(f"❌ Acceptor {self.id} REJECTS Proposal {proposal_id} (Already Promised {self.promised_id})")
        return False, self.accepted_id, self.accepted_value

    def accept(self, proposal_id, value):
        """
        Handles the Accept phase.
        :param proposal_id: Proposal ID from the Proposer.
        :param value: Value being proposed.
        :return: Boolean indicating whether the value was accepted.
        """
        if proposal_id >= self.promised_id:
            self.accepted_id = proposal_id
            self.accepted_value = value
            print(f"🎯 Acceptor {self.id} ACCEPTS Proposal {proposal_id} with Value: {value}")
            return True
        
        print(f"❌ Acceptor {self.id} REJECTS Accept({proposal_id}, {value}) (Promised ID: {self.promised_id})")
        return False

class Proposer:
    def __init__(self, id, acceptors):
        self.id = id
        self.acceptors = acceptors
        self.proposal_id = random.randint(1, 100)

    def propose(self, value):
        """ Executes Paxos rounds. """
        print(f"\n🚀 Proposer {self.id} STARTS Paxos with Proposal ID {self.proposal_id}")
        
        promises = []
        for acceptor in self.acceptors:
            success, _, _ = acceptor.prepare(self.proposal_id)
            if success:
                promises.append(acceptor)

        if len(promises) < len(self.acceptors) // 2 + 1:
            print(f"❌ Not enough promises received. Proposal {self.proposal_id} FAILED.\n")
            return None  
        
        accepted_count = 0
        for acceptor in promises:
            if acceptor.accept(self.proposal_id, value):
                accepted_count += 1

        if accepted_count >= len(self.acceptors) // 2 + 1:
            print(f"🏆 CONSENSUS REACHED: {value} (Proposal {self.proposal_id})\n")
            return value
        else:
            print(f"⚠️ Proposal {self.proposal_id} FAILED in Accept Phase.\n")
            return None

class Learner:
    def __init__(self):
        self.final_value = None

    def learn(self, value):
        """ Stores the final agreed-upon value. """
        self.final_value = value
        print(f"📚 LEARNER: Final decision is '{value}'\n")

# Set the number of acceptors
NUM_ACCEPTORS = 5

# All Acceptors function correctly (no failures)
acceptors = [Acceptor(i) for i in range(NUM_ACCEPTORS)]

# Create proposer and learner
proposer = Proposer(1, acceptors)
learner = Learner()

# Run Paxos Consensus
final_value = proposer.propose("X=10")
if final_value:
    learner.learn(final_value)
