# MARL Benchmark Adaptation Guide for POLLN

**Supplementary Document to Experimental Validation Framework**
**Date:** 2026-03-06

---

## Overview

This document provides detailed technical specifications for adapting standard Multi-Agent Reinforcement Learning (MARL) benchmarks to POLLN's architecture, along with implementation guidance for the novel metrics proposed in the main experimental framework.

---

## Part 1: Standard MARL Benchmarks

### 1.1 SMAC (StarCraft Multi-Agent Challenge)

#### Original Specification

**Paper**: Samvelyan, M., et al. (2019). "The StarCraft Multi-Agent Challenge." arXiv:1902.04043.

**Key Features**:
- Based on Blizzard's StarCraft II game engine
- Micromanagement scenarios with 2-30 agents
- Decentralized execution with partial observability
- Cooperative tasks requiring coordination

**Standard Scenarios**:
1. **Corridor**: Marines must navigate a corridor while avoiding enemy fire
2. **3m**: 3 Marines vs 3 enemy Marines (symmetric)
3. **2s3z**: 2 Stalkers + 3 Zealots vs enemy units (heterogeneous)
4. **MMM**: Marines, Marauders, Medivacs (combined arms)

**Standard Metrics**:
- Win rate
- Episode length
- Damage dealt
- Units lost

#### POLLN Adaptation

**Agent Mapping**:

| POLLN Specialist | SMAC Unit Type | Rationale |
|------------------|----------------|-----------|
| Combat Agent | Marines, Stalkers, Zealots | Direct combat |
| Support Agent | Medivacs | Healing support |
| Tactical Agent | Marauders | Armored combat |
| Navigator Agent | All units | Positioning |
| Coordinator Agent | All units | Coordination |

**Architecture Modifications**:

```python
class POLLN_SMAC_Agent:
    """
    POLLN agent adapted for SMAC environment
    """
    def __init__(self, specialist_type, unit_type):
        self.specialist_type = specialist_type
        self.unit_type = unit_type
        self.sensors = [
            'unit_position',      # Self position
            'enemy_positions',    # Visible enemies
            'ally_positions',     # Visible allies
            'health',             # Current health
            'cooldowns',          # Ability cooldowns
        ]
        self.outputs = [
            'move_direction',     # Where to move
            'attack_target',      # What to attack
            'ability_use',        # Special abilities
        ]

    def get_observation(self, env_state):
        """Extract local observation for this agent"""
        # Partial observability: only see nearby units
        local_obs = extract_local_environment(
            env_state,
            self.unit_type,
            radius=OBSERVATION_RADIUS
        )
        return local_obs

    def select_action(self, obs, available_actions):
        """Select action via SPORE protocol and Plinko"""
        # 1. Publish observation to SPORE topics
        self.publish_observation(obs)

        # 2. Receive proposals from specialists
        proposals = self.receive_proposals()

        # 3. Plinko stochastic selection
        selected_action = self.plinko.select(proposals)

        return selected_action
```

**Modified Metrics for POLLN**:

1. **Emergence Coefficient (EC)**:
   ```python
   EC = (Colony_Win_Rate - Best_Individual_Win_Rate) / Best_Individual_Win_Rate
   ```

2. **Synergy Index (SI)**:
   ```python
   SI = (Colony_Performance - Sum_Individual_Performances) / Sum_Individual_Performances
   ```

3. **Coordination Efficiency (CE)**:
   ```python
   CE = (Successful_Coordinated_Attacks / Total_Attacks)
   ```

4. **Specialization Score (SS)**:
   ```python
   SS = Variance(Agent_Behavior_Diversity)
   ```

**Experimental Setup**:

```python
# Colony configurations to test
colony_configs = [
    {
        'name': 'homogeneous_small',
        'agents': [CombatAgent] * 3,
        'count': 3
    },
    {
        'name': 'heterogeneous_small',
        'agents': [CombatAgent, SupportAgent, TacticalAgent],
        'count': 3
    },
    {
        'name': 'heterogeneous_medium',
        'agents': [CombatAgent]*5 + [SupportAgent]*2 + [TacticalAgent]*3,
        'count': 10
    },
    {
        'name': 'heterogeneous_large',
        'agents': [CombatAgent]*10 + [SupportAgent]*5 + [TacticalAgent]*5 + [NavigatorAgent]*5,
        'count': 25
    }
]
```

**Implementation Timeline**: 4 weeks
- Week 1: Environment setup and agent mapping
- Week 2: SPORE protocol integration
- Week 3: Plinko layer integration
- Week 4: Metrics implementation and testing

---

### 1.2 MPE (Multi-Agent Particle Environment)

#### Original Specification

**Paper**: Lowe, R., et al. (2017). "Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments." NeurIPS.

**Key Features**:
- 2D continuous space with point-mass physics
- Communication-based scenarios
- Simple, interpretable dynamics
- Fast training (minutes to hours)

**Standard Scenarios**:
1. **Simple Spread**: Agents must spread out and cover landmarks
2. **Simple Reference**: One agent must communicate landmark info to others
3. **Simple Push**: Agents must push a box to a landmark
4. **Cooperative Navigation**: Agents must navigate to goals without colliding

**Standard Metrics**:
- Episode reward
- Communication efficiency
- Collision rate
- Task completion time

#### POLLN Adaptation

**Communication Mapping to SPORE**:

| MPE Communication | SPORE Topic | POLLN Specialist |
|-------------------|-------------|------------------|
| Physical observation | `sensor/data` | VisionAgent |
| Communication message | `comms/outbound` | CommunicationAgent |
| Goal information | `planning/goal` | PlannerAgent |
| Action selection | `action/selected` | ExecutorAgent |

**Agent Implementation**:

```python
class POLLN_MPE_Agent:
    """
    POLLN agent for MPE environment
    """
    def __init__(self, agent_id, specialist_type, world_dims):
        self.agent_id = agent_id
        self.specialist_type = specialist_type
        self.position = np.random.rand(2) * world_dims
        self.velocity = np.zeros(2)

        # SPORE topics for MPE
        self.topics = {
            'sensor/data': 'sensor_observations',
            'comms/outbound': 'inter_agent_messages',
            'comms/inbound': 'received_messages',
            'planning/goal': 'target_goals',
            'action/selected': 'final_actions'
        }

    def sense(self, world_state):
        """Gather local information"""
        obs = {
            'position': self.position,
            'velocity': self.velocity,
            'nearby_agents': self._get_nearby_agents(world_state),
            'landmarks': world_state['landmarks'],
            'goals': world_state['goals']
        }
        return obs

    def communicate(self, message):
        """Publish message to SPORE topic"""
        self.publish(self.topics['comms/outbound'], {
            'sender_id': self.agent_id,
            'message': message,
            'timestamp': time.time()
        })

    def receive_messages(self):
        """Get messages from other agents"""
        messages = self.subscribe(self.topics['comms/inbound'])
        return messages

    def plan(self, obs, messages):
        """Generate action proposals"""
        # Different specialists propose different actions
        proposals = []

        if self.specialist_type == 'navigator':
            proposals.append(self._navigate_proposal(obs))
        elif self.specialist_type == 'communicator':
            proposals.append(self._communicate_proposal(messages))
        elif self.specialist_type == 'collaborator':
            proposals.append(self._collaborate_proposal(obs, messages))

        return proposals

    def act(self, selected_proposal):
        """Execute selected action"""
        self.position += selected_proposal['velocity']
        return selected_proposal
```

**POLLN-Specific Metrics**:

1. **Stigmergy Score (StS)**: Indirect coordination through environment
   ```python
   def stigmergy_score(trajectory_history):
       """Measure indirect coordination (no direct communication)"""
       # Count successful coordination without direct messages
       indirect_coord = count_coordination_without_comms(trajectory_history)
       total_coord = count_total_coordination(trajectory_history)
       return indirect_coord / total_coord
   ```

2. **Communication Efficiency (ComE)**: Information per bit
   ```python
   def communication_efficiency(messages, performance):
       """Performance achieved per message sent"""
       return performance / len(messages)
   ```

3. **Emergent Protocols (EmP)**: Discovered communication patterns
   ```python
   def emergent_protocols(message_history):
       """Count discovered communication patterns"""
       # Cluster message patterns
       patterns = cluster_messages(message_history)
       return len(patterns)
   ```

**Experimental Scenarios**:

```python
# Test communication scenarios
comm_scenarios = [
    {
        'name': 'no_communication',
        'enabled': False,
        'hypothesis': 'POLLN can coordinate without explicit communication'
    },
    {
        'name': 'limited_communication',
        'enabled': True,
        'bandwidth': 1,  # 1 message per step
        'hypothesis': 'Limited communication improves coordination'
    },
    {
        'name': 'full_communication',
        'enabled': True,
        'bandwidth': float('inf'),
        'hypothesis': 'Full communication maximizes performance'
    },
    {
        'name': 'learned_communication',
        'enabled': True,
        'learned': True,
        'hypothesis': 'Learned communication protocols outperform fixed'
    }
]
```

**Implementation Timeline**: 3 weeks
- Week 1: MPE environment setup and POLLN integration
- Week 2: Communication protocol implementation
- Week 3: Metrics and testing

---

### 1.3 Google Research Football

#### Original Specification

**Paper**: Liu, Y., et al. (2019). "Google Research Football: A Novel Reinforcement Learning Environment." AAAI.

**Key Features**:
- Football simulation based on real game engine
- 11 vs 11 players (or smaller for academy scenarios)
- Complex, strategic coordination
- Real-time decision making

**Standard Academy Scenarios**:
1. **3vs1**: 3 attackers vs 1 defender
2. **Counterattack**: Transition from defense to attack
3. **Pass & Shoot**: Team play to score

**Standard Metrics**:
- Win rate
- Goal difference
- Pass completion rate
- Shot accuracy

#### POLLN Adaptation

**Position-Based Specialization**:

| Football Position | POLLN Specialist | Responsibilities |
|-------------------|------------------|------------------|
| Goalkeeper | Defensive Specialist | Shot blocking, distribution |
| Defenders | Defensive Coordinator | Marking, tackling, positioning |
| Midfielders | Tactical Coordinator | Passing, playmaking, transition |
| Forwards | Offensive Specialist | Shooting, positioning, pressing |
| All | Strategic Coordinator | Overall formation and tactics |

**Emergent Strategy Detection**:

```python
def detect_emergent_strategies(match_history):
    """
    Detect strategies that emerge from agent interactions
    """
    strategies = {
        'formation': detect_formation(match_history),
        'pressing': detect_pressing(match_history),
        'passing_patterns': detect_passing_patterns(match_history),
        'transition_play': detect_transitions(match_history),
        'set_pieces': detect_set_pieces(match_history)
    }
    return strategies

def detect_formation(match_history):
    """
    Detect team formation from player positions
    """
    positions = extract_player_positions(match_history)

    # Cluster positions to identify formation
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=4)  # Defenders, mids, forwards, goalkeeper
    clusters = kmeans.fit_predict(positions)

    # Identify formation (4-4-2, 4-3-3, etc.)
    formation = identify_formation(clusters)

    return formation

def detect_passing_patterns(match_history):
    """
    Detect emergent passing patterns
    """
    passes = extract_passes(match_history)

    patterns = {
        'possession_based': compute_possession_style(passes),
        'direct_play': compute_directness(passes),
        'width': compute_width(passes),
        'tempo': compute_tempo(passes)
    }

    return patterns
```

**POLLN-Specific Metrics**:

1. **Strategic Emergence (StrE)**: Novel strategies discovered
   ```python
   strategic_emergence = len(discovered_strategies) / baseline_strategies
   ```

2. **Coordination Quality (CQ)**: Team coordination score
   ```python
   def coordination_quality(match_events):
       """Measure coordination quality"""
       aspects = {
           'passing_accuracy': count_successful_passes() / total_passes,
           'offside_success': count_successful_offside_traps() / total_offside_attempts,
           'pressing_coordination': measure_pressing_synchronization(),
           'transition_speed': measure_counterattack_speed()
       }
       return mean(aspects.values())
   ```

3. **Adaptive Tactics (AT)**: Tactical flexibility
   ```python
   def adaptive_tactics(match_history, opponent_strength):
       """Measure tactical adaptation"""
       # Does team adjust tactics based on opponent?
       tactical_changes = count_tactical_shifts(match_history)
       correlation = correlate_with_opponent(tactical_changes, opponent_strength)
       return correlation
   ```

**Implementation Timeline**: 5 weeks
- Week 1-2: Environment setup and agent mapping
- Week 3: Strategy detection implementation
- Week 4: Metrics implementation
- Week 5: Testing and validation

---

## Part 2: Novel POLLN Benchmarks

### 2.1 Dynamic Role Formation Benchmark

#### Objective

Test whether initially identical agents spontaneously discover and coordinate around specialized roles.

#### Environment Specification

```python
class DynamicRoleEnvironment:
    """
    Environment where agents must discover roles to solve task
    """
    def __init__(self, num_agents=10, num_roles=3):
        self.num_agents = num_agents
        self.num_roles = num_roles
        self.agents = [IdenticalAgent() for _ in range(num_agents)]

        # Define roles (unknown to agents initially)
        self.roles = {
            'collector': {
                'capability': 'collect_resources',
                'color': 'blue',
                'efficiency': 1.0
            },
            'processor': {
                'capability': 'process_resources',
                'color': 'green',
                'efficiency': 1.0
            },
            'transporter': {
                'capability': 'transport_resources',
                'color': 'red',
                'efficiency': 1.0
            }
        }

        # Task requirements
        self.task = {
            'collect_needed': 100,
            'process_needed': 100,
            'transport_needed': 100
        }

    def step(self, actions):
        """
        Execute one step of environment

        Agents discover roles through:
        1. Trying different actions
        2. Receiving feedback on efficiency
        3. Observing other agents' successes
        4. Coordinating to avoid redundancy
        """
        # Execute actions
        results = [self.agent_act(agent, action) for agent, action in zip(self.agents, actions)]

        # Provide feedback
        for agent, result in zip(self.agents, results):
            agent.receive_feedback(result)

        # Measure role formation
        role_assignments = self.infer_roles()

        # Check task completion
        task_complete = self.check_task_completion()

        return {
            'observations': [agent.get_observation() for agent in self.agents],
            'rewards': [self.compute_reward(agent, result) for agent, result in zip(self.agents, results)],
            'role_assignments': role_assignments,
            'task_complete': task_complete
        }

    def infer_roles(self):
        """
        Infer which agents have taken which roles
        Based on recent behavior
        """
        role_assignments = {}

        for agent in self.agents:
            # Analyze recent actions
            recent_actions = agent.get_recent_actions(n=50)

            # Match to roles
            role_scores = {}
            for role_name, role_spec in self.roles.items():
                score = self.match_actions_to_role(recent_actions, role_spec)
                role_scores[role_name] = score

            # Assign to highest-scoring role
            assigned_role = max(role_scores, key=role_scores.get)
            role_assignments[agent.id] = assigned_role

        return role_assignments
```

#### Metrics

1. **Role Specialization Score (RSS)**:
   ```python
   def role_specialization_score(behaviors, role_assignments):
       """
       High RSS: Agents within same role are similar
       Low RSS: Agents across roles are similar
       """
       # Compute within-role similarity
       within_sim = []
       for role in set(role_assignments.values()):
           role_agents = [a for a, r in role_assignments.items() if r == role]
           role_behaviors = [behaviors[a] for a in role_agents]
           sim = avg_pairwise_similarity(role_behaviors)
           within_sim.append(sim)

       # Compute between-role similarity
       between_sim = []
       roles = list(set(role_assignments.values()))
       for i, role1 in enumerate(roles):
           for role2 in roles[i+1:]:
               agents1 = [a for a, r in role_assignments.items() if r == role1]
               agents2 = [a for a, r in role_assignments.items() if r == role2]
               behaviors1 = [behaviors[a] for a in agents1]
               behaviors2 = [behaviors[a] for a in agents2]
               sim = avg_pairwise_similarity(behaviors1, behaviors2)
               between_sim.append(sim)

       RSS = np.mean(within_sim) / (np.mean(between_sim) + epsilon)
       return RSS
   ```

2. **Role Stability Index (RSI)**:
   ```python
   def role_stability_index(role_history):
       """
       Measure how stable role assignments are over time
       """
       # Compute change point detection
       changes = count_role_changes(role_history)

       # Stability = 1 - (changes / total possible changes)
       RSI = 1 - (changes / len(role_history))
       return RSI
   ```

3. **Emergent Role Count (ERC)**:
   ```python
   def emergent_role_count(behaviors, max_roles=10):
       """
       Count distinct roles that have emerged
       """
       # Cluster behaviors
       from sklearn.cluster import KMeans, silhouette_score

       best_k = 1
       best_score = -1

       for k in range(2, min(max_roles, len(behaviors))):
           kmeans = KMeans(n_clusters=k)
           labels = kmeans.fit_predict(behaviors)
           score = silhouette_score(behaviors, labels)

           if score > best_score:
               best_score = score
               best_k = k

       return best_k
   ```

**Implementation Timeline**: 4 weeks

---

### 2.2 Non-Stationary Adaptation Benchmark

#### Environment Specification

```python
class NonStationaryEnvironment:
    """
    Environment that changes over time
    """
    def __init__(self, change_types=['reward', 'dynamics', 'topology']):
        self.change_types = change_types
        self.current_phase = 0
        self.phase_length = 1000  # episodes

        # Phase configurations
        self.phases = [
            {
                'reward_function': self.reward_phase_1,
                'transition_dynamics': self.dynamics_phase_1,
                'agent_connectivity': self.topology_phase_1
            },
            {
                'reward_function': self.reward_phase_2,
                'transition_dynamics': self.dynamics_phase_2,
                'agent_connectivity': self.topology_phase_2
            },
            # ... more phases
        ]

    def step(self, state, action):
        """
        Execute step in current phase
        """
        # Check for phase change
        if self.episode_count % self.phase_length == 0:
            self.change_phase()

        # Get current phase configuration
        phase = self.phases[self.current_phase]

        # Execute action
        reward = phase['reward_function'](state, action)
        next_state = phase['transition_dynamics'](state, action)

        return next_state, reward, self.check_done(next_state)

    def change_phase(self):
        """
        Change to next phase (environment change)
        """
        self.current_phase = (self.current_phase + 1) % len(self.phases)

        # Log change for analysis
        self.phase_history.append({
            'episode': self.episode_count,
            'old_phase': self.current_phase - 1,
            'new_phase': self.current_phase,
            'change_type': self.phases[self.current_phase]['change_type']
        })
```

#### Metrics

1. **Adaptation Speed (AS)**:
   ```python
   def adaptation_speed(performance_history, change_points, recovery_threshold=0.9):
       """
       Episodes to recover to 90% of pre-change performance
       """
       adaptation_speeds = []

       for change_point in change_points:
           pre_performance = np.mean(performance_history[max(0, change_point-100):change_point])
           target_performance = recovery_threshold * pre_performance

           for t in range(change_point, len(performance_history)):
               if performance_history[t] >= target_performance:
                   adaptation_speeds.append(t - change_point)
                   break

       return np.mean(adaptation_speeds)
   ```

2. **Forgetting Severity (FS)**:
   ```python
   def forgetting_severity(performance_history, change_points):
       """
       Maximum performance drop after change
       """
       severities = []

       for change_point in change_points:
           pre_performance = np.mean(performance_history[max(0, change_point-100):change_point])

           # Find minimum performance in window after change
           window = performance_history[change_point:change_point+100]
           min_performance = np.min(window)

           severity = (pre_performance - min_performance) / pre_performance
           severities.append(severity)

       return np.mean(severities)
   ```

3. **Diversity-Adaptation Correlation (DAC)**:
   ```python
   def diversity_adaptation_correlation(diversity_history, adaptation_speeds):
       """
       Correlation between diversity and adaptation speed
       """
       # Align diversity measurements with adaptation events
       aligned_diversity = [diversity_history[i] for i in range(0, len(diversity_history), 1000)]

       correlation = np.corrcoef(aligned_diversity, adaptation_speeds)[0, 1]
       return correlation
   ```

**Implementation Timeline**: 3 weeks

---

## Part 3: Evaluation Infrastructure

### 3.1 Experiment Runner

```python
class ExperimentRunner:
    """
    Infrastructure for running POLLN experiments
    """
    def __init__(self, config):
        self.config = config
        self.results = []
        self.checkpoints = []

    def run_experiment(self, experiment_fn, num_seeds=10):
        """
        Run experiment with multiple random seeds
        """
        for seed in range(num_seeds):
            # Set random seed
            set_seed(seed)

            # Run experiment
            result = experiment_fn(seed=seed)

            # Store result
            self.results.append({
                'seed': seed,
                'result': result,
                'timestamp': time.time()
            })

            # Checkpoint
            if len(self.results) % 5 == 0:
                self.checkpoint()

        return self.results

    def analyze_results(self):
        """
        Compute statistics across seeds
        """
        # Extract metrics
        metrics = {}
        for result in self.results:
            for metric_name, metric_value in result['result'].items():
                if metric_name not in metrics:
                    metrics[metric_name] = []
                metrics[metric_name].append(metric_value)

        # Compute statistics
        analysis = {}
        for metric_name, values in metrics.items():
            analysis[metric_name] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'ci': confidence_interval(values),
                'min': np.min(values),
                'max': np.max(values)
            }

        return analysis
```

### 3.2 Metrics Computation

```python
class MetricsComputer:
    """
    Compute POLLN-specific metrics
    """
    @staticmethod
    def emergence_coefficiency(colony_performance, individual_performances):
        """EC = (Colony - BestIndividual) / BestIndividual"""
        best_individual = np.max(individual_performances)
        ec = (colony_performance - best_individual) / best_individual
        return ec

    @staticmethod
    def synergy_index(colony_performance, individual_performances):
        """SI = (Colony - Sum) / Sum"""
        sum_individuals = np.sum(individual_performances)
        si = (colony_performance - sum_individuals) / sum_individuals
        return si

    @staticmethod
    def super_linear_scaling(agent_counts, performances):
        """Fit power law: Performance = a * N^b, return b"""
        log_n = np.log(agent_counts)
        log_perf = np.log(performances)
        b, _ = np.polyfit(log_n, log_perf, 1)
        return b

    @staticmethod
    def trace_completeness(traceable_decisions, total_decisions):
        """TCI = traceable / total"""
        tci = traceable_decisions / total_decisions
        return tci

    @staticmethod
    def recovery_time(performance_history, perturbation_time, recovery_threshold=0.9):
        """Episodes to recover to threshold * pre-perturbation performance"""
        pre_performance = np.mean(performance_history[:perturbation_time])
        target = recovery_threshold * pre_performance

        for t in range(perturbation_time, len(performance_history)):
            if performance_history[t] >= target:
                return t - perturbation_time

        return float('inf')  # Never recovered
```

### 3.3 Visualization

```python
class ResultsVisualizer:
    """
    Visualize experimental results
    """
    @staticmethod
    def plot_emergence(results, output_path):
        """Plot emergence metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Emergence Coefficient
        axes[0, 0].bar(['POLLN', 'Baseline'], [results['polln_ec'], results['baseline_ec']])
        axes[0, 0].set_title('Emergence Coefficient')
        axes[0, 0].set_ylabel('EC')

        # Synergy Index
        axes[0, 1].bar(['POLLN', 'Baseline'], [results['polln_si'], results['baseline_si']])
        axes[0, 1].set_title('Synergy Index')
        axes[0, 1].set_ylabel('SI')

        # Scaling
        agent_counts = results['agent_counts']
        performances = results['performances']
        axes[1, 0].plot(agent_counts, performances, 'o-')
        axes[1, 0].set_xlabel('Agent Count')
        axes[1, 0].set_ylabel('Performance')
        axes[1, 0].set_title('Scaling Behavior')
        axes[1, 0].set_xscale('log')

        # Emergent Capabilities
        axes[1, 1].bar(['POLLN', 'Baseline'], [results['polln_ecc'], results['baseline_ecc']])
        axes[1, 1].set_title('Emergent Capabilities')
        axes[1, 1].set_ylabel('Count')

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_adaptation(results, output_path):
        """Plot adaptation to non-stationary environments"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Performance over time
        axes[0].plot(results['performance_history'])
        for change_point in results['change_points']:
            axes[0].axvline(x=change_point, color='red', linestyle='--', alpha=0.5)
        axes[0].set_xlabel('Episode')
        axes[0].set_ylabel('Performance')
        axes[0].set_title('Performance in Non-Stationary Environment')

        # Diversity vs Adaptation
        axes[1].scatter(results['diversity'], results['adaptation_speed'])
        axes[1].set_xlabel('Diversity')
        axes[1].set_ylabel('Adaptation Speed')
        axes[1].set_title('Diversity-Adaptation Correlation')

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
```

---

## Part 4: Implementation Guidelines

### 4.1 Code Structure

```
polln_experiments/
├── benchmarks/
│   ├── smac/
│   │   ├── __init__.py
│   │   ├── environment.py
│   │   ├── agents.py
│   │   └── metrics.py
│   ├── mpe/
│   │   ├── __init__.py
│   │   ├── environment.py
│   │   ├── agents.py
│   │   └── metrics.py
│   └── football/
│       ├── __init__.py
│       ├── environment.py
│       ├── agents.py
│       └── metrics.py
├── novel_benchmarks/
│   ├── role_formation/
│   ├── non_stationary/
│   └── fault_injection/
├── metrics/
│   ├── emergence.py
│   ├── traceability.py
│   ├── durability.py
│   └── safety.py
├── infrastructure/
│   ├── runner.py
│   ├── checkpointing.py
│   └── visualization.py
└── configs/
    ├── experiments.yaml
    └── benchmarks.yaml
```

### 4.2 Configuration Management

```yaml
# configs/experiments.yaml
experiments:
  emergence_benchmark:
    name: "Emergence Benchmark"
    duration_weeks: 12
    benchmarks:
      - smac
      - mpe
      - football
    metrics:
      - emergence_coefficient
      - synergy_index
      - super_linear_scaling
      - emergent_capability_count
    seeds: 50
    colony_configs:
      - homogeneous_small
      - heterogeneous_small
      - heterogeneous_medium
      - heterogeneous_large

  stochastic_vs_deterministic:
    name: "Stochastic vs Deterministic Selection"
    duration_weeks: 8
    environments:
      - non_stationary_bandit
      - varying_reward_task
    metrics:
      - cumulative_regret
      - adaptation_speed
      - diversity_maintenance
    seeds: 30
    temperature_configs:
      - 0.1
      - 0.5
      - 1.0
      - 3.0
      - 5.0
```

---

## Part 5: Validation Checklist

### Before Running Experiments

- [ ] Benchmarks implemented and tested
- [ ] Baseline systems verified
- [ ] Metrics computation validated
- [ ] Random seed system working
- [ ] Data logging functional
- [ ] Checkpointing system tested
- [ ] Visualization pipeline ready
- [ ] Statistical analysis planned

### During Experiments

- [ ] Monitor for anomalies
- [ ] Check resource usage
- [ ] Verify data quality
- [ ] Document unexpected behaviors
- [ ] Regular checkpointing

### After Experiments

- [ ] Data integrity verified
- [ ] Outliers documented
- [ ] Statistical tests applied
- [ ] Effect sizes computed
- [ ] Confidence intervals calculated
- [ ] Results visualized
- [ ] Report generated

---

**Document Status**: Complete
**Related Documents**:
- Main experimental framework: `round2-experimental-design.md`
- Executive summary: `round2-experimental-design-summary.md`

**Next Steps**:
1. Review with research team
2. Begin implementation of infrastructure
3. Implement priority benchmarks (SMAC, MPE)
4. Validate metrics computation

**Author**: Experimental Validation Designer
**Date**: 2026-03-06
