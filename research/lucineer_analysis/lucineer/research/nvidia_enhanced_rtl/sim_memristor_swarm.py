import numpy as np
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, state):
        self.state = state
        self.neighbors = []

    def interact(self, other_agent):
        if self.state == other_agent.state:
            return
        elif self.state == -1 and other_agent.state == 1:
            self.state = 0
        elif self.state == 1 and other_agent.state == -1:
            self.state = 0
        elif self.state == 0 and other_agent.state == -1:
            self.state = -1
        elif self.state == 0 and other_agent.state == 1:
            self.state = 1

    def update(self):
        for neighbor in self.neighbors:
            self.interact(neighbor)

class Swarm:
    def __init__(self, num_agents):
        self.agents = [Agent(np.random.choice([-1, 0, 1])) for _ in range(num_agents)]
        for i in range(num_agents):
            self.agents[i].neighbors = [self.agents[(i-1)%num_agents], self.agents[(i+1)%num_agents]]

    def update(self):
        for agent in self.agents:
            agent.update()

    def get_states(self):
        return [agent.state for agent in self.agents]

num_agents = 100
num_iterations = 100

swarm = Swarm(num_agents)
states_over_time = np.zeros((num_iterations, num_agents))

for i in range(num_iterations):
    swarm.update()
    states_over_time[i] = swarm.get_states()

plt.imshow(states_over_time, cmap='bwr', interpolation='nearest')
plt.show()