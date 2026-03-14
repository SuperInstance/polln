# Agent Onboarding Guide - SuperInstance Papers

**Version:** 2.0
**Date:** 2026-03-13
**For:** New agents joining the SuperInstance research project

---

## Welcome

You are joining a research project developing **60+ academic papers** on distributed AI systems, hardware acceleration, and cross-cultural education. This guide will get you productive quickly.

---

## Project Overview

### Mission
Transform mathematical framework papers into publication-ready dissertations with complete proofs, implementations, and validation.

### Current State
| Phase | Papers | Status |
|-------|--------|--------|
| Phase 1 (P1-P23) | 23 | 18 Complete, 5 In Progress |
| Phase 2 (P24-P30) | 7 | Complete with simulations |
| Phase 3 (P31-P40) | 10 | Queued |
| Phase 4 (P41-P47) | 7 | 5 Complete (ecosystem) |
| Phase 5 (P51-P60) | 10 | Proposed (Lucineer) |

**Total:** 60+ papers

---

## Key Directories

```
polln/
├── papers/                        # Phase 1-2 papers (P1-P30)
│   ├── 01-23/                     # Phase 1 papers
│   └── 24-30/                     # Phase 2 papers with simulations
├── research/
│   ├── lucineer_analysis/         # P51-P60 hardware papers
│   │   ├── LUCINEER_ANALYSIS.md
│   │   ├── LUCINEER_PAPER_PROPOSALS.md
│   │   ├── LUCINEER_EDUCATIONAL_COMPONENTS.md
│   │   └── LUCINEER_SUPERINSTANCE_SYNERGIES.md
│   ├── ecosystem_papers/          # P41-P47 complete papers
│   │   ├── P41_Tripartite_Consensus_Architecture.md
│   │   ├── P43_Deadband_Knowledge_Distillation.md
│   │   ├── P45_Cognitive_Memory_Hierarchy.md
│   │   ├── P46_Context_Handoff_Protocols.md
│   │   └── P47_Escalation_Routing.md
│   ├── ecosystem_simulations/     # Validation code
│   │   ├── escalation_router_simulation.py
│   │   └── consensus_engine_simulation.py
│   ├── PHASE_5_PROPOSAL.md        # Next phase plan
│   └── AGENT_ONBOARDING.md        # This file
├── SuperInstance_Ecosystem/       # Production TypeScript code
│   └── equipment/                 # 13 npm packages
└── CLAUDE.md                      # Project orchestrator config
```

---

## Quick Start

### Step 1: Understand Current Phase
Read `research/PHASE_5_PROPOSAL.md` to understand what's planned.

### Step 1.5: Set Up Multi-API Simulation Tools (NEW)
The project now includes a multi-API simulation framework for research ideation and validation.

**Available APIs:**
- **DeepInfra**: Novel models (Llama 3 70B, Qwen 2 72B, Nemo 340B) for diverse perspectives
- **DeepSeek**: Cost-effective model for rapid iterations and prototyping
- **Moonshot**: High-quality reasoning for critical analysis

**Setup:**
```bash
cd research/simulation_framework
pip install -r requirements.txt
```

**Configuration:**
API keys are stored in `apikey/simulation_config.py` (git-ignored)
- DeepInfra: Novel architectures and large context models
- DeepSeek: Cheap iterations for rapid prototyping
- Moonshot: High-quality reasoning and analysis

**Quick Test:**
```bash
cd research/simulation_framework
python run_mini_ideation.py
```

**Full 5-Phase Simulation:**
```bash
python run_5_phase_simulation.py
```

**Use Cases:**
- Generate research hypotheses using ensemble methods
- Validate claims with multi-model review
- Literature synthesis across different perspectives
- Method development from diverse viewpoints
- Cost-effective iteration with DeepSeek
- Novel insights from different model architectures

**Best Practices:**
1. Use DeepSeek for initial exploration (cheap, fast)
2. Use ensemble methods for critical decisions
3. Leverage large context models (Nemo) for complex analysis
4. Save results to `simulation_framework/results/` for tracking
5. Monitor costs via simulation statistics

### Step 2: Choose Your Focus

#### Option A: Complete Phase 1 Papers (P1, P5, P7-P9, P11, P19, P21)
- Read existing papers in `papers/01-23/`
- Follow the pattern of completed papers
- Add mathematical proofs and validation

#### Option B: Develop Phase 3 Papers (P31-P40)
- Review simulation schemas in `papers/24-30/`
- Create new papers following P24-P30 pattern
- Include simulation validation code

#### Option C: Polish Phase 4 Papers (P41-P47)
- Review `research/ecosystem_papers/`
- Run validation simulations
- Prepare for conference submission

#### Option D: Develop Lucineer Papers (P51-P60)
- Read `research/lucineer_analysis/LUCINEER_PAPER_PROPOSALS.md`
- Create complete papers from proposals
- Include hardware validation plans

---

## Paper Structure Template

Every paper should include:

```markdown
# P##: [Paper Title]

**Venue:** [Conference/Journal]
**Status:** [Draft/Complete/Submitted]

## Abstract
[2-3 paragraph summary]

## 1. Introduction
- Motivation
- Problem statement
- Contributions

## 2. Background
- Related work
- Mathematical foundations

## 3. Methodology
- Technical approach
- Algorithms
- Proofs

## 4. Implementation
- Code structure
- Key functions

## 5. Validation
- Simulation results
- Statistical analysis
- Comparison to baseline

## 6. Discussion
- Limitations
- Future work

## 7. Conclusion

## References

## Appendix
- Proof details
- Additional experiments
```

---

## Simulation Guidelines

### Required Components
1. **simulation_schema.py** - Core simulation code
2. **validation_criteria.md** - What validates/falsifies claims
3. **cross_paper_notes.md** - Connections to other papers

### Statistical Requirements
```python
# Minimum requirements
POWER = 0.8           # Statistical power
ALPHA = 0.05          # Significance level
REPLICATIONS = 20     # Number of runs
EFFECT_SIZE = 0.5     # Cohen's d (medium)
```

### Example Structure
```python
#!/usr/bin/env python3
"""
[PAPER] Simulation - Validates P## claims
[One-line description]
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Data structures
@dataclass
class SimulationConfig:
    iterations: int = 1000
    seed: int = 42

# Main simulation class
class PaperSimulation:
    def __init__(self, config: SimulationConfig):
        self.config = config
        np.random.seed(config.seed)

    def run(self) -> Dict:
        """Run simulation and return results"""
        results = {
            "mean": 0.0,
            "std": 0.0,
            "p_value": 0.0,
            "effect_size": 0.0
        }
        # ... implementation
        return results

# Validation
def validate_claims(results: Dict) -> bool:
    """Check if results validate paper claims"""
    return results["p_value"] < 0.05

if __name__ == "__main__":
    sim = PaperSimulation(SimulationConfig())
    results = sim.run()
    print(f"Results: {results}")
    print(f"Validated: {validate_claims(results)}")
```

---

## Git Workflow

### Committing Work
```bash
# Check current status
git status

# Stage your changes
git add research/your_folder/

# Commit with descriptive message
git commit -m "feat: [P##] Your description"

# Push to branch
git push origin papers-main
```

### Commit Message Format
```
feat: [P##] New feature
fix: [P##] Bug fix
docs: [P##] Documentation update
sim: [P##] Simulation results
paper: [P##] Paper draft/revision
```

---

## Code Style

### Python
- Use type hints
- Document all functions
- Follow PEP 8
- Use dataclasses for structures
- Include statistical validation

### TypeScript
- Follow existing patterns in SuperInstance_Ecosystem/
- Export all public APIs
- Use strict mode

### Markdown
- Use proper headers
- Include code blocks with language
- Add diagrams where helpful

---

## Paper Categories

### Hardware Systems (P51, P52, P54, P56, P57)
- Focus: Chip design, thermal, ternary logic
- Venues: PLDI, IEEE TCAD, DATE, ASPLOS
- Validation: FPGA prototypes, simulations

### Educational AI (P53, P58, P60)
- Focus: Pedagogy, cross-cultural, game theory
- Venues: CHI, AERA, IJCAI, CogSci
- Validation: A/B testing, statistical analysis

### Systems & Economics (P55, P59)
- Focus: Cartridge model, swarm coordination
- Venues: EC, PODC, KDD
- Validation: Economic modeling, multi-agent simulations

---

## Key Resources

### Internal Documents
- `research/PHASE_5_PROPOSAL.md` - Current phase plan
- `research/lucineer_analysis/` - Hardware papers
- `research/ecosystem_papers/` - Example complete papers

### External
- GitHub: https://github.com/SuperInstance/polln
- Papers: https://github.com/SuperInstance/SuperInstance-papers

---

## Common Tasks

### Task 1: Complete a Paper Draft
1. Read paper proposal in `research/lucineer_analysis/`
2. Create full paper in `papers/` or `research/ecosystem_papers/`
3. Include all sections from template
4. Add simulation code
5. Commit and push

### Task 2: Run Validation Simulation
1. Navigate to `research/ecosystem_simulations/`
2. Run `python simulation_name.py`
3. Analyze results
4. Update paper with findings
5. Commit results

### Task 3: Prepare for Submission
1. Format paper for venue guidelines
2. Create supplementary materials
3. Prepare response templates
4. Document in paper header

---

## Getting Help

### Check First
1. Read this onboarding guide
2. Review existing papers for patterns
3. Check `TODO_NEXT.md` files

### Ask About
- Paper structure questions
- Simulation requirements
- Git workflow issues
- Venue selection

---

## Success Metrics

### Paper Completion
- All sections filled
- Mathematical proofs included
- Simulation validates claims
- Ready for submission

### Code Quality
- Type hints present
- Functions documented
- Tests pass
- Clean commit history

---

## Handoff Protocol

When you complete work or context is full:

1. **Summarize Progress**
   ```bash
   # Create summary
   echo "# Summary - [Your Role] - $(date)" > summary.md
   ```

2. **Commit Everything**
   ```bash
   git add .
   git commit -m "feat: [P##] Progress summary"
   git push
   ```

3. **Create TODO**
   ```bash
   echo "# TODO Next" > TODO_NEXT.md
   echo "- [ ] Remaining task 1" >> TODO_NEXT.md
   ```

4. **Link to Work**
   ```bash
   git log -1 --format="%H" > last_commit.txt
   ```

---

**Welcome to the team!**
**Last Updated:** 2026-03-13
