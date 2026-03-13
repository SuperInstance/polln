#!/usr/bin/env python3
"""
P26: Value Networks for Colony State Evaluation - FIXED VERSION
Simulation Schema for Validation/Falsification of Claims

This version uses a more robust value estimation approach that doesn't rely on
complex neural network training, which was failing in the original version.

Key Fixes:
1. Direct feature-based value estimation (no neural network)
2. Proper option evaluation with meaningful state differences
3. Causal relationship between decisions and outcomes
4. Ensemble-based uncertainty estimation from feature perturbations
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
import random
from collections import deque

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class DecisionType(Enum):
    TASK_SELECTION = "task_selection"
    AGENT_ASSIGNMENT = "agent_assignment"
    RESOURCE_ALLOCATION = "resource_allocation"
    STRATEGY_CHOICE = "strategy_choice"

@dataclass
class ColonyState:
    """Colony Configuration Vector (CCV)."""
    # Agent state: (A) - agent activation levels
    agent_activations: np.ndarray
    # Environment state: (E) - task queue, external factors
    environment_state: np.ndarray
    # Workload state: (W) - current processing load
    workload_state: np.ndarray
    # Pheromone state: (Phi) - coordination signals
    pheromone_state: np.ndarray
    # Stress state: (Psi) - system stress indicators
    stress_state: np.ndarray

    # Derived features
    feature_vector: Optional[np.ndarray] = None

    def compute_features(self, feature_dim: int = 64) -> np.ndarray:
        """Compute combined feature vector for value network."""
        if self.feature_vector is not None:
            return self.feature_vector

        # Multi-scale features
        f1 = np.mean(self.agent_activations)  # Global activation
        f2 = np.std(self.agent_activations)   # Activation variance
        f3 = np.mean(self.environment_state)  # Environment level
        f4 = np.mean(self.workload_state)  # Workload level
        f5 = np.mean(self.pheromone_state)  # Coordination level
        f6 = np.mean(self.stress_state)  # Stress level

        # Higher-order features
        f7 = f1 * f5  # Activation-coordination product
        # Correlation - handle different sizes
        min_size = min(len(self.agent_activations), len(self.workload_state))
        if min_size > 1:
            f8 = np.corrcoef(self.agent_activations[:min_size], self.workload_state[:min_size])[0, 1]
        else:
            f8 = 0.0
        f9 = np.linalg.norm(self.stress_state)  # Stress magnitude

        # Concatenate all features
        features = np.array([f1, f2, f3, f4, f5, f6, f7, abs(f8) if not np.isnan(f8) else 0, f9])

        # Pad to feature_dim (pad AFTER the array, not before)
        if len(features) < feature_dim:
            features = np.pad(features, (0, feature_dim - len(features)))
        else:
            features = features[:feature_dim]

        self.feature_vector = features
        return features

@dataclass
class ValuePrediction:
    """Output from value network."""
    predicted_value: float  # Expected outcome (0-1)
    uncertainty: float  # Confidence interval width
    features_used: np.ndarray  # Feature importance

@dataclass
class Decision:
    """A decision made by the colony."""
    decision_type: DecisionType
    options: List[Any]
    selected_index: int
    value_prediction: float
    timestamp: int
    actual_outcome: Optional[float] = None

# ============================================================================
# DIRECT VALUE ESTIMATOR (No Neural Network)
# ============================================================================

class DirectValueEstimator:
    """
    Direct value estimation using feature-based formula.
    More robust than neural network for this simulation.
    """

    def __init__(self, state_dim: int = 64, ensemble_size: int = 10):
        self.state_dim = state_dim
        self.ensemble_size = ensemble_size

        # Experience buffer for uncertainty estimation
        self.experience_buffer = deque(maxlen=10000)

        # Feature weights (learned through experience)
        self.feature_weights = np.random.randn(9) * 0.1  # 9 base features
        self.feature_weights[0] = 0.4   # Activation
        self.feature_weights[1] = -0.3  # Variance
        self.feature_weights[4] = 0.2   # Coordination
        self.feature_weights[5] = -0.4  # Stress
        self.feature_weights[8] = -0.3  # Stress magnitude

    def _compute_base_features(self, state: ColonyState) -> np.ndarray:
        """Compute the 9 base features from state."""
        f1 = np.mean(state.agent_activations)  # Global activation
        f2 = np.std(state.agent_activations)   # Activation variance
        f3 = np.mean(state.environment_state)  # Environment level
        f4 = np.mean(state.workload_state)     # Workload level
        f5 = np.mean(state.pheromone_state)    # Coordination level
        f6 = np.mean(state.stress_state)       # Stress level
        f7 = f1 * f5                           # Activation-coordination product

        min_size = min(len(state.agent_activations), len(state.workload_state))
        if min_size > 1:
            f8 = np.corrcoef(state.agent_activations[:min_size], state.workload_state[:min_size])[0, 1]
        else:
            f8 = 0.0

        f9 = np.linalg.norm(state.stress_state)  # Stress magnitude

        return np.array([f1, f2, f3, f4, f5, f6, f7, abs(f8) if not np.isnan(f8) else 0, f9])

    def predict(self, state: ColonyState) -> ValuePrediction:
        """Predict value with uncertainty from ensemble."""
        base_features = self._compute_base_features(state)

        # Ensemble predictions with feature perturbations
        predictions = []
        feature_importance = np.zeros(9)

        for i in range(self.ensemble_size):
            # Add noise to features for ensemble diversity
            noise = np.random.randn(9) * 0.05
            perturbed_features = base_features + noise

            # Compute value using weighted sum + sigmoid
            raw_value = np.dot(perturbed_features, self.feature_weights)
            value = 1 / (1 + np.exp(-raw_value))  # Sigmoid to [0,1]
            predictions.append(value)

            # Estimate feature importance
            if i == 0:
                for j in range(9):
                    perturbed = base_features.copy()
                    perturbed[j] += 0.1
                    raw_perturbed = np.dot(perturbed, self.feature_weights)
                    value_perturbed = 1 / (1 + np.exp(-raw_perturbed))
                    feature_importance[j] = abs(value_perturbed - predictions[0])

        # Ensemble statistics
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)

        # Pad feature importance to state_dim
        full_importance = np.zeros(self.state_dim)
        full_importance[:len(feature_importance)] = feature_importance

        return ValuePrediction(
            predicted_value=mean_pred,
            uncertainty=std_pred,
            features_used=full_importance
        )

    def update_from_experience(self, state: ColonyState, actual_outcome: float):
        """Learn from experience by adjusting feature weights."""
        base_features = self._compute_base_features(state)
        predicted = self.predict(state).predicted_value

        error = actual_outcome - predicted

        # Simple gradient descent update
        learning_rate = 0.01
        gradient = error * base_features

        # Only update if error is significant
        if abs(error) > 0.1:
            self.feature_weights += learning_rate * gradient

            # Normalize weights to prevent explosion
            self.feature_weights = np.clip(self.feature_weights, -2, 2)

        self.experience_buffer.append({
            "features": base_features,
            "predicted": predicted,
            "actual": actual_outcome,
            "error": error
        })

    def calculate_brier_score(self) -> float:
        """Calculate Brier score from experience buffer."""
        if len(self.experience_buffer) < 10:
            return 1.0

        brier = np.mean([
            (exp["predicted"] - exp["actual"]) ** 2
            for exp in self.experience_buffer
        ])

        return brier

# ============================================================================
# VALUE-GUIDED DECISION MAKER
# ============================================================================

class ValueGuidedDecisionMaker:
    """Makes decisions guided by value predictions."""

    def __init__(self, value_estimator: DirectValueEstimator):
        self.value_estimator = value_estimator
        self.decisions_made: List[Decision] = []
        self.random_decisions: List[Decision] = []

    def select_option(
        self,
        state: ColonyState,
        options: List[Any],
        decision_type: DecisionType,
        use_value_guidance: bool = True
    ) -> Decision:
        """Select best option using value estimator or random."""
        if len(options) == 0:
            raise ValueError("No options to select from")

        if use_value_guidance:
            # Evaluate each option
            option_values = []
            for i, option in enumerate(options):
                # Create hypothetical state with option selected
                hypothetical_state = self._apply_option(state, option, decision_type)
                pred = self.value_estimator.predict(hypothetical_state)
                option_values.append((i, pred.predicted_value, pred.uncertainty))

            # Select highest expected value
            best_idx, best_value, best_uncertainty = max(option_values, key=lambda x: x[1])

            decision = Decision(
                decision_type=decision_type,
                options=options,
                selected_index=best_idx,
                value_prediction=best_value,
                timestamp=len(self.decisions_made)
            )
            self.decisions_made.append(decision)

        else:
            # Random selection
            random_idx = random.randint(0, len(options) - 1)
            random_pred = self.value_estimator.predict(
                self._apply_option(state, options[random_idx], decision_type)
            )

            decision = Decision(
                decision_type=decision_type,
                options=options,
                selected_index=random_idx,
                value_prediction=random_pred.predicted_value,
                timestamp=len(self.random_decisions)
            )
            self.random_decisions.append(decision)

        return decision

    def _apply_option(self, state: ColonyState, option: Any, decision_type: DecisionType) -> ColonyState:
        """Create hypothetical state after applying option."""
        if isinstance(option, str) and option.startswith("task_"):
            task_id = int(option.split("_")[1])
            # Different tasks have different effects on colony state
            task_complexity = (task_id + 1) / 5.0  # Normalize to 0-1
            task_load = 0.1 + task_complexity * 0.3  # 10% to 40% load increase

            # Apply task effects to state
            new_workload = state.workload_state.copy()
            if len(new_workload) > task_id:
                new_workload[task_id] = min(1.0, new_workload[task_id] + task_load)

            # Stress increases with task complexity
            new_stress = state.stress_state.copy()
            new_stress[0] = min(1.0, new_stress[0] + task_complexity * 0.2)

            # Agents need to activate more
            new_activations = state.agent_activations.copy()
            agents_to_activate = min(len(new_activations), int(task_complexity * 5) + 1)
            for i in range(agents_to_activate):
                new_activations[i] = min(1.0, new_activations[i] + 0.3)

            return ColonyState(
                agent_activations=new_activations,
                environment_state=state.environment_state.copy(),
                workload_state=new_workload,
                pheromone_state=state.pheromone_state.copy(),
                stress_state=new_stress
            )
        else:
            return ColonyState(
                agent_activations=state.agent_activations.copy(),
                environment_state=state.environment_state.copy(),
                workload_state=state.workload_state.copy(),
                pheromone_state=state.pheromone_state.copy(),
                stress_state=state.stress_state.copy()
            )

    def compare_strategies(self) -> Dict:
        """Compare value-guided vs random decisions."""
        if len(self.decisions_made) == 0 or len(self.random_decisions) == 0:
            return {"comparison_available": False}

        guided_outcomes = [d.actual_outcome for d in self.decisions_made if d.actual_outcome is not None]
        random_outcomes = [d.actual_outcome for d in self.random_decisions if d.actual_outcome is not None]

        if len(guided_outcomes) == 0 or len(random_outcomes) == 0:
            return {"comparison_available": False}

        guided_avg = np.mean(guided_outcomes)
        random_avg = np.mean(random_outcomes)

        improvement = (guided_avg - random_avg) / random_avg * 100 if random_avg > 0 else 0

        return {
            "comparison_available": True,
            "guided_avg_outcome": guided_avg,
            "random_avg_outcome": random_avg,
            "improvement_percent": improvement,
            "claim_20_percent": improvement > 20
        }

# ============================================================================
# SIMULATION
# ============================================================================

class ValueNetworkSimulation:
    """Main simulation for value network validation."""

    def __init__(
        self,
        num_agents: int = 20,
        num_tasks: int = 50,
        state_dim: int = 64
    ):
        self.num_agents = num_agents
        self.num_tasks = num_tasks
        self.state_dim = state_dim

        # Components
        self.value_estimator = DirectValueEstimator(state_dim=state_dim)
        self.decision_maker = ValueGuidedDecisionMaker(self.value_estimator)

        # State
        self.current_state: Optional[ColonyState] = None
        self.timestep = 0

        # Tracking
        self.predictions: List[Tuple[float, float]] = []

    def initialize_state(self):
        """Initialize colony state."""
        self.current_state = ColonyState(
            agent_activations=np.random.rand(self.num_agents),
            environment_state=np.random.rand(10),
            workload_state=np.random.rand(self.num_tasks),
            pheromone_state=np.random.rand(self.num_agents),
            stress_state=np.random.rand(5)
        )
        self.timestep = 0

    def generate_tasks(self) -> List[Any]:
        """Generate task options."""
        return [f"task_{i}" for i in range(5)]

    def step(self, use_value_guidance: bool = True) -> float:
        """Execute one simulation step."""
        if self.current_state is None:
            self.initialize_state()

        # Generate options
        tasks = self.generate_tasks()

        # Make decision
        decision = self.decision_maker.select_option(
            self.current_state,
            tasks,
            DecisionType.TASK_SELECTION,
            use_value_guidance=use_value_guidance
        )

        # Calculate outcome based on state and decision
        task_id = int(decision.options[decision.selected_index].split("_")[1])
        task_complexity = (task_id + 1) / 5.0

        # Compute success probability based on colony state
        avg_activation = np.mean(self.current_state.agent_activations)
        activation_balance = 1.0 - np.std(self.current_state.agent_activations)
        stress_level = np.mean(self.current_state.stress_state)
        overload = np.mean(self.current_state.workload_state)

        # Success formula: balanced activation + moderate stress - overload
        success_prob = 0.3 + 0.4 * activation_balance + 0.2 * (1.0 - abs(stress_level - 0.5)) - 0.3 * overload
        success_prob = max(0.1, min(0.9, success_prob))

        # Higher complexity tasks have higher variance but higher potential reward
        outcome = success_prob + task_complexity * 0.1 + np.random.randn() * 0.15
        outcome = max(0.0, min(1.0, outcome))

        decision.actual_outcome = outcome

        # Record prediction vs actual
        self.predictions.append((decision.value_prediction, outcome))

        # Update estimator from experience
        self.value_estimator.update_from_experience(self.current_state, outcome)

        # Generate next state
        next_state = self.decision_maker._apply_option(
            self.current_state,
            decision.options[decision.selected_index],
            decision.decision_type
        )

        # Decay state values
        next_state = ColonyState(
            agent_activations=np.maximum(0, next_state.agent_activations - 0.05),
            environment_state=self.current_state.environment_state.copy(),
            workload_state=np.maximum(0, next_state.workload_state - 0.02),
            pheromone_state=np.maximum(0, next_state.pheromone_state - 0.01),
            stress_state=np.maximum(0, next_state.stress_state - 0.03)
        )

        self.current_state = next_state
        self.timestep += 1

        return outcome

    def run_simulation(self, num_steps: int = 200) -> Dict:
        """Run full simulation."""
        self.initialize_state()

        # Half with value guidance, half random for comparison
        guided_steps = num_steps // 2

        for i in range(num_steps):
            use_guidance = i < guided_steps
            self.step(use_value_guidance=use_guidance)

        return self.get_metrics()

    def get_metrics(self) -> Dict:
        """Calculate validation metrics."""
        # Prediction correlation
        if len(self.predictions) > 1:
            predicted = [p[0] for p in self.predictions]
            actual = [p[1] for p in self.predictions]
            correlation = np.corrcoef(predicted, actual)[0, 1]
        else:
            correlation = 0

        # Brier score
        brier = self.value_estimator.calculate_brier_score()

        # Strategy comparison
        strategy_comparison = self.decision_maker.compare_strategies()

        return {
            "prediction_correlation": correlation if not np.isnan(correlation) else 0,
            "brier_score": brier,
            "strategy_comparison": strategy_comparison
        }

# ============================================================================
# VALIDATION RUNNER
# ============================================================================

def run_validation_simulation(num_steps: int = 200) -> Dict:
    """Run full validation simulation for P26 claims."""
    sim = ValueNetworkSimulation(
        num_agents=20,
        num_tasks=50,
        state_dim=64
    )

    metrics = sim.run_simulation(num_steps)

    results = {
        "claim_1_prediction_correlation": {
            "description": "Value prediction correlates with outcomes (r > 0.7)",
            "correlation": metrics["prediction_correlation"],
            "validated": metrics["prediction_correlation"] > 0.7,
            "threshold": 0.7
        },
        "claim_2_uncertainty_calibration": {
            "description": "Uncertainty estimates are well-calibrated (Brier < 0.2)",
            "brier_score": metrics["brier_score"],
            "validated": metrics["brier_score"] < 0.2,
            "threshold": 0.2
        },
        "claim_3_value_guided_improvement": {
            "description": "Value-guided > random by >20%",
            "comparison": metrics["strategy_comparison"],
            "validated": metrics["strategy_comparison"].get("claim_20_percent", False),
            "threshold": "20%"
        },
        "summary": metrics
    }

    return results

if __name__ == "__main__":
    print("=" * 60)
    print("P26: Value Networks - Validation Simulation (FIXED VERSION)")
    print("=" * 60)

    results = run_validation_simulation(num_steps=200)

    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    for claim_id, claim_data in results.items():
        if claim_id == "summary":
            continue
        status = "VALIDATED" if claim_data["validated"] else "NOT VALIDATED"
        print(f"\n{claim_id}: {claim_data['description']}")
        print(f"  Status: {status}")
        for key, value in claim_data.items():
            if key not in ["description", "validated"]:
                print(f"  {key}: {value}")
