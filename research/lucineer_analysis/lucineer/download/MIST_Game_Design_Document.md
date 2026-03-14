# MIST: The Tale of a Sheepdog Puppy
## Game Design Document v1.0

---

## Executive Summary

**Mist** is a voxel-style educational game for ages 5-10 that teaches children (and their parents) about learning, knowledge transfer, and AI concepts through the journey of a sheepdog puppy discovering their place in a working farm.

The game embodies the **Tabula Rosa** concept: the player starts knowing nothing and learns only what the wise Alpha Dog teaches them - just like training a specialized AI model from a neutral substrate.

---

## Core Narrative

### The Story

You are a young sheepdog puppy on a large farm. You don't know who you are, what a farm is, or what dogs do. Through the guidance of **Elder Bark**, the wise Alpha Dog, you discover:

1. **Identity** - You are a dog, part of a working lineage
2. **Purpose** - Your job is to help the farmer with sheep
3. **Family** - Generations of dogs have worked this farm
4. **Trade** - Herding is a skill that takes time to master
5. **Legacy** - Someday you will teach your own puppies

### The Alpha Dog Philosophy

Elder Bark teaches not through dominance, but through respect. He became Alpha because:
- Other dogs trust his judgment
- He's patient, not forceful
- He knows when to lead and when to let others learn
- He represents the distilled wisdom of generations

**Key Teaching:** *"Every master was once an apprentice. Every teacher was once a student."*

---

## Gameplay Mechanics

### Level Structure

| Level | Title | Role | Learning Focus |
|-------|-------|------|----------------|
| 0 | Apprentice | Puppy | Learning the trade (10,000 hours) |
| 1 | Journeyman | Working Dog | Training puppies |
| 2 | Master | Alpha | Managing trainers |
| 3 | Elder | Wisdom Council | Higher abstractions |

### Level 0: Apprentice (The Core Game)

**Starting State:** Complete Tabula Rosa - the player knows nothing.

**Progressive Revelation Topics:**

1. **IDENTITY**
   - You are a dog
   - You live in a kennel with other dogs
   - This is a farm
   - Farms have animals

2. **SHEEP**
   - Sheep are gentle creatures
   - They follow each other (flocking)
   - We guide them to good grass
   - Scared sheep run together

3. **RAMS** (Edge Cases)
   - Not all sheep are the same
   - Rams have horns
   - Rams can be stubborn
   - Patience, not force

4. **WORK** (The Trade)
   - Every dog has a job
   - My job is to teach, yours to learn
   - Work helps the farm family
   - Good work takes time

5. **FAMILY** (Knowledge Distillation)
   - Your mother was a great working dog
   - Many generations before
   - Each learns from the previous
   - Someday you'll teach your puppies

### Seasonal Gameplay

| Season | Activities | Challenges |
|--------|-----------|------------|
| Spring | Lambs born, learn herding | Young animals are unpredictable |
| Summer | Full farm work, hot days | Heat management, water sources |
| Autumn | Harvest time, sheep shearing | Busy season, many tasks |
| Winter | Protect animals, limited grazing | Cold, snow, shelter |

### Core Actions

1. **EXPLORE** - Move through the voxel farm world
2. **DISCOVER** - Find new animals, locations, objects
3. **LEARN** - Elder Bark reveals knowledge
4. **HERD** - Guide sheep to designated areas
5. **PROTECT** - Keep animals safe from threats
6. **TEACH** (Level 1+) - Train puppies

---

## The Tabula Rosa Connection

### For Children

The game teaches that:
- Learning is gradual and cumulative
- Teachers deserve respect
- Everyone starts knowing nothing
- Practice makes you better
- One day you can teach others

### For Parents (The AI Layer)

Hidden in the gameplay are core AI/ML concepts:

| Game Element | AI Concept |
|--------------|------------|
| Puppy = Blank slate | **Tabula Rosa model** |
| Elder Bark = Teacher | **Training data / supervision** |
| Progressive revelation | **Curriculum learning** |
| Generations of dogs | **Knowledge distillation** |
| Rams vs Sheep | **Edge cases / adversarial examples** |
| Seasons | **Training epochs** |
| Mastery = Alpha | **Convergence / optimization** |
| Teaching puppies | **Model fine-tuning / LoRA** |

### Parent Layer Toggle

Parents can enable an overlay that explains:
- What AI concept the current activity represents
- How this maps to real machine learning
- Discussion questions to ask their child

---

## World Design

### Voxel Art Style

- **Aesthetic:** Minecraft-meets-children's-book
- **Colors:** Warm, pastoral palette
- **Scale:** Friendly, approachable proportions
- **Characters:** Expressive, non-threatening

### Locations

1. **Kennel** - Home base, where Elder Bark teaches
2. **Pasture** - Where sheep graze
3. **Barn** - Shelter for animals
4. **Farmhouse** - Where the farmer lives
5. **Woods** - Edge of farm, occasional discoveries
6. **Stream** - Water source
7. **Hill** - Vantage point for herding

### Characters

| Character | Role | Personality |
|-----------|------|-------------|
| **Elder Bark** | Alpha Dog | Wise, patient, gentle |
| **Mist** | Player Puppy | Curious, eager to learn |
| **Swift** | Senior Dog | Fast, teaches advanced herding |
| **Gentle** | Mid-level Dog | Patient, good with lambs |
| **Pip** | Peer Puppy | Playful, learning alongside you |
| **Farmer** | Human | Kind, provides food/shelter |

### Animals

| Animal | Behavior | Challenge Level |
|--------|----------|-----------------|
| **Sheep** | Follow each other, easily guided | Easy |
| **Lambs** | Playful, wander off | Medium |
| **Rams** | Stubborn, need patience | Hard |
| **Chickens** | Scatter randomly, harmless | Easy |
| **Cows** | Slow, need wide spaces | Medium |
| **Ducks** | Need water, flock to ponds | Medium |

---

## Dialogue System

### Elder Bark's Teaching Style

```
EXAMPLE DIALOGUE:

[Player approaches sheep for the first time]

ELDER BARK:
"Ah, you've found the sheep. Good eyes, young one."

[Reveal dialogue box]
"These are sheep. They are gentle creatures."
"They follow each other - see how they move together?"

[Insight tag]
💡 Insight: Flocking behavior

[Continue button]
"That's your first lesson. Sheep stay together.
We guide them, not chase them."

[Acknowledge button: "I understand"]
```

### Progressive Complexity

| Discovery Level | Teaching Style |
|-----------------|----------------|
| First encounter | Full explanation |
| Second encounter | Reminder + question |
| Third encounter | Brief check-in |
| Mastered | Occasional praise |

---

## Progression System

### Metrics

1. **Wisdom Points** - Earned through learning
2. **Herding Score** - Successfully guided animals
3. **Trust Level** - Built through consistent work
4. **Teaching Hours** - (Level 1+) Puppies trained

### Unlockables

| Requirement | Unlock |
|-------------|--------|
| 10 Wisdom Points | Access to far pasture |
| 50 Herding Score | Swift becomes available mentor |
| 100 Trust | Introduction to rams |
| 1000 Wisdom Points | Level up to Journeyman |

---

## Level 1: Journeyman

Once the player has mastered Level 0:

### New Mechanics

1. **TRAIN PUPPIES** - Guide new puppies like Elder Bark guided you
2. **CREATE LESSONS** - Design training sequences
3. **ASSESS PROGRESS** - Evaluate puppy learning
4. **ADAPT TEACHING** - Different puppies need different approaches

### Tabula Rosa Layer

Players now experience both sides:
- They remember being the learner
- They now create the curriculum
- They see why patience matters

### AI Connection

This maps to:
- Training new models
- Creating training data
- Hyperparameter tuning
- Model evaluation

---

## Level 2+: Master & Elder

Higher levels introduce:

- **Managing multiple trainers** (model orchestration)
- **Farm-wide decisions** (system architecture)
- **Wisdom council** (ensemble methods)
- **Legacy planning** (model succession)

---

## Technical Implementation

### Current Prototype Features

- ✅ Voxel grid world display
- ✅ Player movement (keyboard + click)
- ✅ Alpha Dog dialogue system
- ✅ Progressive teaching reveals
- ✅ Discovery tracking
- ✅ Season system
- ✅ Parent layer toggle

### Planned Features

- [ ] Animated voxel characters
- [ ] Actual sheep herding mechanics
- [ ] Sound design & music
- [ ] Save game progress
- [ ] Multiple puppy training (Level 1)
- [ ] Achievement system
- [ ] Parent-child co-op mode

---

## Educational Value

### For Ages 5-7

- Basic cause and effect
- Following directions
- Animal care empathy
- Patience and practice

### For Ages 8-10

- Understanding trade mastery
- Mentorship concepts
- Leadership through respect
- Legacy and generational knowledge

### For Parents

- Understanding AI training concepts
- Discussion starters about learning
- Connection to platform's chip design mission
- Bonding through shared gameplay

---

## Connection to Lucineer Platform

| Game Concept | Platform Concept |
|--------------|------------------|
| Puppy learning | New AI model training |
| Elder Bark | Pre-trained foundation model |
| Herding mastery | Inference chip specialization |
| Teaching puppies | LoRA adapter training |
| Farm = world | Mask-locked inference chip |

**The game is the onboarding for understanding what Lucineer does.**

---

## Credits

**Concept:** Based on "Mist: The Tale of a Sheepdog Puppy" film
**Educational Framework:** Lucineer Tabula Rosa Research
**Voxel Art Direction:** Lucineer Design Team

---

*Document Version 1.0*
*Last Updated: 2026*
