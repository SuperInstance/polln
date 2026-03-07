# FPIC Implementation Protocol for POLLN
## Free, Prior, and Informed Consent for Indigenous Knowledge Attribution

**Document Type:** Research & Implementation Specification
**Author:** FPIC Implementation Specialist (Round 2)
**Date:** 2026-03-06
**Status:** Active Protocol
**Version:** 1.0

---

## Executive Summary

This document provides a comprehensive protocol for implementing Free, Prior, and Informed Consent (FPIC) for indigenous knowledge attribution in the POLLN project. It synthesizes international frameworks (UNDRIP), emerging best practices (CARE Principles for Indigenous Data Governance), and technical implementation guidance for AI systems working with cultural knowledge.

**Critical Recognition:** FPIC is not a checklist - it's an ongoing relationship with indigenous communities grounded in respect, reciprocity, and self-determination.

---

## Table of Contents

1. [FPIC Framework: UNDRIP Foundations](#fpic-framework)
2. [CARE Principles for Indigenous Data Governance](#care-principles)
3. [Traditional Knowledge Labels & Attribution Systems](#tk-labels)
4. [Access Control & Cultural Protocols](#access-control)
5. [Community Engagement Guide](#community-engagement)
6. [Technical Implementation Protocol](#technical-implementation)
7. [Case Studies: Lessons Learned](#case-studies)
8. [Compliance Checklist](#compliance-checklist)
9. [Templates & Resources](#templates)

---

## 1. FPIC Framework: UNDRIP Foundations {#fpic-framework}

### 1.1 What is FPIC?

**Free, Prior, and Informed Consent (FPIC)** is a principle recognized in the United Nations Declaration on the Rights of Indigenous Peoples (UNDRIP). It represents the minimum standard for engaging with indigenous peoples regarding projects that affect their rights, lands, territories, and resources.

#### The Four Elements

| Element | Definition | In POLLN Context | Red Flags |
|---------|------------|------------------|-----------|
| **Free** | No coercion, intimidation, manipulation, or undue influence | Keepers/developers opt-in voluntarily | Pressure to adopt features, implicit requirements |
| **Prior** | Sought **before** authorization or commencement of activities | Before using indigenous concepts in code/docs | Retroactive attribution after implementation |
| **Informed** | Full disclosure of nature, size, pace, reversibility, scope | Clear explanation of how knowledge will be used | Vague descriptions, hidden commercial applications |
| **Consent** | Right to say **yes OR no**, including right to withhold | Veto power over use of specific concepts | Assuming consent from silence |

### 1.2 UNDRIP Articles Relevant to POLLN

| Article | Title | Application to POLLN |
|---------|-------|---------------------|
| **Article 11** | Right to practice and revitalize cultural traditions | POLLN must respect cultural protocols around knowledge |
| **Article 12** | Right to maintain, control, and protect cultural heritage | Indigenous communities control their traditional knowledge |
| **Article 19** | States shall consult to obtain FPIC before adopting measures | Before adopting indigenous concepts into system architecture |
| **Article 31** | Right to maintain, control, protect and develop cultural heritage | Traditional knowledge is intellectual property |
| **Article 32** | FPIC required for projects affecting lands/territories | Applied metaphorically to "knowledge territory" |

### 1.3 FPIC vs. Standard Consultation

```
┌─────────────────────────────────────────────────────────────┐
│               FPIC vs. CONSULTATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   CONSULTATION (Insufficient):                              │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • "We're informing you what we're doing"            │  │
│   │ • Community input considered but not binding        │  │
│   │ • Can proceed despite objections                    │  │
│   │ • Often one-time, transactional                     │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   FPIC (Required):                                          │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • "What do YOU think we should do?"                 │  │
│   │ • Community decision is binding                     │  │
│   │ • Cannot proceed without consent                    │  │
│   │ • Ongoing relationship, revocable                   │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. CARE Principles for Indigenous Data Governance {#care-principles}

### 2.1 Overview

The **CARE Principles** were developed by the Global Indigenous Data Alliance (GIDA) and published in 2019 to complement the FAIR principles (Findable, Accessible, Interoperable, Reusable) with emphasis on Indigenous rights and interests.

### 2.2 The Four CARE Principles

#### C - Collective Benefit

**Definition:** Data ecosystems shall be designed and function in ways that enable Indigenous Peoples to derive benefit from the data.

**Implementation in POLLN:**

```yaml
CollectiveBenefit:
  benefit_sharing:
    - revenue_sharing: "Marketplace sales using indigenous knowledge"
    - capacity_building: "Free access to POLLN for indigenous communities"
    - technology_transfer: "Custom deployments for community needs"
    - educational: "Training programs for indigenous technologists"

  community_outcomes:
    - language_preservation: "Tools for indigenous language projects"
    - cultural_continuity: "Support for traditional knowledge systems"
    - sovereignty: "Data infrastructure under community control"

  governance:
    - indigenous_council: "Veto power over feature decisions"
    - benefit_allocation: "Communities decide how benefits are used"
    - transparency: "Public reporting on benefits distributed"
```

**Key Requirements:**
- Benefits must be defined **with** communities, not **for** them
- Benefits must be proportional to use of knowledge
- Financial benefits are necessary but not sufficient
- Capacity building is essential for long-term benefit

#### A - Authority to Control

**Definition:** Indigenous Peoples' rights and interests in Indigenous data must be recognized and their authority to control such data be empowered.

**Implementation in POLLN:**

```python
class IndigenousDataAuthority:
    """
    Implements Indigenous authority over data and knowledge
    """

    def __init__(self):
        self.community_authorities = {
            "haudenosaunee": {
                "authorized_representatives": [],
                "governance_structure": "Longhouse Council",
                "decision_making": "Consensus",
                "scope": ["Distributed governance", "Relational ontology"]
            },
            # Additional communities...
        }

    def check_authority(self, knowledge_id: str,
                        proposed_use: ProposedUse) -> AuthorityCheck:
        """
        Verify whether community has authorized this use
        """
        knowledge = self.get_knowledge(knowledge_id)
        authority = self.community_authorities[knowledge.tradition]

        # Check if representative is authorized
        if not self.is_authorized_representative(proposed_use.approved_by):
            return AuthorityCheck(
                authorized=False,
                reason="Representative not authorized by community"
            )

        # Check if use is within agreed scope
        if proposed_use.type not in authority.scope:
            return AuthorityCheck(
                authorized=False,
                reason="Use outside agreed scope"
            )

        return AuthorityCheck(authorized=True)

    def grant_authority(self, tradition: str,
                       representative: str,
                       scope: List[str]) -> None:
        """
        Record community's designation of authorized representative
        """
        # This must be initiated by community, not POLLN
        self.community_authorities[tradition].authorized_representatives.append(
            {
                "representative": representative,
                "credentials": "Verified by community governance",
                "scope": scope,
                "term": "As determined by community"
            }
        )
```

**Key Requirements:**
- Communities designate their own representatives
- Authority cannot be assumed or unilaterally granted
- Control extends to derivative works and applications
- Authority includes right to revoke access

#### R - Responsibility

**Definition:** Those working with Indigenous data have a responsibility to share how those data are used to support Indigenous Peoples' self-determination and collective benefit.

**Implementation in POLLN:**

```yaml
ResponsibilityFramework:
  transparency_requirements:
    - usage_reports: "Quarterly reports to communities on knowledge use"
    - impact_assessments: "Annual assessment of cultural impacts"
    - public_accounting: "Public report on indigenous engagement"

  relationship_obligations:
    - ongoing_consultation: "Regular check-ins, not one-time consent"
    - reciprocity: "Give back to knowledge communities"
    - accountability: "Respond to community concerns"

  documentation_requirements:
    - provenance: "Track all uses of indigenous knowledge"
    - attribution: "Credit sources in all documentation"
    - conditions: "Document and enforce consent conditions"
```

**Key Requirements:**
- Transparency is not optional - it's a core obligation
- Reports must be accessible (language, format, timing)
- Responsibility continues for the lifetime of the project
- Includes responsibility for downstream uses

#### E - Ethics

**Definition:** Indigenous Peoples' rights and wellbeing should be the primary concern at all stages of the data life cycle and across the data ecosystem.

**Implementation in POLLN:**

```python
class EthicalFramework:
    """
    Ethical guardrails for indigenous knowledge in POLLN
    """

    ETHICAL_PRINCIPLES = [
        "do_no_harm",
        "cultural_safety",
        "context_integrity",
        "future_generations",
        "intergenerational_accountability"
    ]

    def ethical_review(self, proposal: KnowledgeUseProposal) -> Review:
        """
        Review proposal for ethical concerns
        """
        concerns = []

        # Principle: Do No Harm
        harm_assessment = self.assess_potential_harm(proposal)
        if harm_assessment.risk_level > "low":
            concerns.append({
                "principle": "do_no_harm",
                "concern": f"Risk level: {harm_assessment.risk_level}",
                "mitigation_required": True
            })

        # Principle: Cultural Safety
        if self.trivializes_culture(proposal):
            concerns.append({
                "principle": "cultural_safety",
                "concern": "Use may trivialize sacred concepts",
                "mitigation_required": True
            })

        # Principle: Context Integrity
        if self.removes_from_context(proposal):
            concerns.append({
                "principle": "context_integrity",
                "concern": "Use removes knowledge from cultural context",
                "mitigation_required": True
            })

        # Principle: Future Generations
        if self.limits_future_use(proposal):
            concerns.append({
                "principle": "future_generations",
                "concern": "Use may constrain future generations' options",
                "mitigation_required": True
            })

        return Review(
            approved=len(concerns) == 0,
            concerns=concerns,
            conditions=self.generate_mitigation_conditions(concerns)
        )
```

**Key Requirements:**
- Ethics review happens BEFORE any use
- Community wellbeing trumps technical or commercial interests
- When in doubt, the conservative choice is no use
- Ethics cannot be outsourced to checklist - requires judgment

---

## 3. Traditional Knowledge Labels & Attribution Systems {#tk-labels}

### 3.1 Traditional Knowledge (TK) Labels

**Traditional Knowledge Labels** were developed by Local Contexts (localcontexts.org) to help Indigenous communities manage cultural heritage and data. They provide a framework for communicating protocols for access, use, and attribution.

#### TK Label Categories

| Label Type | Purpose | POLLN Equivalent |
|------------|---------|------------------|
| **TK Attribution** | Ensures proper attribution to community | Required for all indigenous knowledge |
| **TK Non-Commercial** | Restricts commercial use | Conditional on community agreement |
| **TK Community Voice** | Allows community perspectives | Community feedback mechanisms |
| **TK Multiple Communities** | Knowledge from multiple sources | Multi-source attribution |
| **TK Culturally Sensitive** | Flags sensitive materials | Sensitivity classification system |
| **TK Secret/Sacred** | Restricted ceremonial knowledge | Absolute restriction level |

### 3.2 POLLN Attribution System

#### Metadata Schema

```typescript
interface IndigenousKnowledgeMetadata {
  // Core identification
  knowledge_id: string;
  concept_name: string;
  source_tradition: string;
  language: string;

  // FPIC status
  fpic_status: "pending" | "approved" | "restricted" | "denied" | "withdrawn";
  fpic_date: Date;
  fpic_representative: string;
  fpic_conditions: string[];

  // Classification
  sensitivity_level: "public" | "attributed" | "restricted" | "sacred" | "forbidden";
  tk_labels: TKLabel[];

  // Attribution
  attribution_statement: string;
  community_name: string;
  community_region: string;

  // Usage tracking
  use_cases: UseCase[];
  last_reviewed: Date;
  expires?: Date;

  // Benefit sharing
  benefit_sharing_active: boolean;
  benefit_sharing_details?: BenefitSharing;
}

interface TKLabel {
  label_type: string;
  applies_to: string[];
  explanation: string;
  community_defined: boolean;
}

interface UseCase {
  component: string;
  feature: string;
  date_adopted: Date;
  approved_by: string;
}
```

#### Attribution Statement Template

```markdown
## Indigenous Knowledge Attribution

This [component/feature/documentation] incorporates [CONCEPT NAME],
which originates from [TRADITION NAME] knowledge systems.

### Source Recognition

We acknowledge that [CONCEPT NAME] is traditional knowledge that has
been stewarded by [COMMUNITY NAME] for [TIME PERIOD]. This knowledge
comes from [SPECIFIC CULTURAL CONTEXT].

### Use Permission

[One of the following]:
- Used with permission from [COMMUNITY/REPRESENTATIVE]
- Used in accordance with FPIC protocol dated [DATE]
- Approved under conditions: [LIST CONDITIONS]
- Public domain concept with attribution provided

### Commitments

We are committed to:
- Respecting the full cultural context of this knowledge
- Honoring any restrictions or conditions on its use
- Sharing benefits with the source community
- Ongoing consultation with community representatives
- Immediate cessation of use if requested by community

### Concerns or Questions

If you are a member of [COMMUNITY NAME] or have concerns about this
use of traditional knowledge, please contact: [CONTACT]

### Learn More

- Indigenous Knowledge Protocol: [LINK]
- FPIC Status: [LINK TO CONSENT RECORD]
- Community Resources: [LINK IF APPLICABLE]
```

### 3.3 Automated Attribution Injection

```python
class AttributionInjector:
    """
    Automatically injects attribution into POLLN outputs
    """

    def inject_into_code(self, code: str,
                         knowledge_ids: List[str]) -> str:
        """
        Add attribution comments to code using indigenous knowledge
        """
        attribution_blocks = []

        for kid in knowledge_ids:
            metadata = self.get_metadata(kid)

            block = f"""
# Indigenous Knowledge Attribution
# Concept: {metadata.concept_name}
# Tradition: {metadata.source_tradition}
# Used with permission under FPIC protocol dated {metadata.fpic_date}
# See [full attribution link] for details
"""
            attribution_blocks.append(block)

        # Insert at top of file
        return "\n".join(attribution_blocks) + "\n\n" + code

    def inject_into_docs(self, docs: str,
                         knowledge_ids: List[str]) -> str:
        """
        Add attribution section to documentation
        """
        metadata_list = [self.get_metadata(kid) for kid in knowledge_ids]

        attribution_section = """
## Indigenous Knowledge Attribution

This work incorporates concepts from multiple cultural traditions.

"""

        for md in metadata_list:
            attribution_section += f"""
### {md.concept_name}

**Source:** {md.source_tradition}
**Status:** {md.fpic_status}
{md.attribution_statement}

"""

        return docs + attribution_section

    def inject_into_ui(self, component: UIComponent,
                       knowledge_ids: List[str]) -> UIComponent:
        """
        Add attribution to UI components (as tooltips, footnotes, etc.)
        """
        # Add subtle attribution markers
        # Don't disrupt user experience but make attribution available
        pass
```

---

## 4. Access Control & Cultural Protocols {#access-control}

### 4.1 Cultural Restriction Levels

```python
class RestrictionLevel(Enum):
    """
    Levels of restriction for indigenous knowledge
    """
    PUBLIC = "public"  # Can be used freely with attribution
    ATTRIBUTED = "attributed"  # Can be used with attribution
    RESTRICTED = "restricted"  # Limited use, specific conditions
    SACRED = "sacred"  # Community approval required
    FORBIDDEN = "forbidden"  # Must not be used
```

#### Access Control Matrix

| Restriction Level | Code Use | Documentation | Public Communication | Commercial Use |
|------------------|----------|---------------|----------------------|----------------|
| **PUBLIC** | Allowed with attribution | Allowed with attribution | Allowed with attribution | Allowed |
| **ATTRIBUTED** | Allowed with attribution | Allowed with attribution | Allowed with attribution | With conditions |
| **RESTRICTED** | With specific conditions | With specific conditions | Limited description | Only if approved |
| **SACRED** | Only if FPIC approved | Only if FPIC approved | Only if FPIC approved | Requires explicit approval |
| **FORBIDDEN** | Never allowed | Never allowed | Never allowed | Never allowed |

### 4.2 Tikanga & Cultural Protocols

**Tikanga** (Māori) refers to the customary system of values and practices that have developed over time and are deeply embedded in the social context.

#### General Cultural Protocol Principles

```yaml
CulturalProtocols:
  general_principles:
    - respect: "Show respect for knowledge and its source"
    - humility: "Acknowledge you are a guest in this knowledge"
    - patience: "Relationships develop over time"
    - reciprocity: "Give back, don't just take"
    - accountability: "Answer to the community"

  protocol_examples:
    maori:
      - manaakitanga: "Care and respect for hosts and guests"
      - kaitiakitanga: "Stewardship, guardianship of knowledge"
      - whanaungatanga: "Building relationships through shared experience"
      - tikanga: "Proper protocols must be observed"

    lakota:
      - mitakuye oyasin: "All my relations - interconnectedness"
      - wolakota: "Peace and harmony in relationships"
      - tiwahe: "Family and community prioritized over individual"
      - ceremonial_knowledge: "Respected as sacred and restricted"

    haudenosaunee:
      - great_law_of_peace: "Consensus-based governance"
      - thanksgiving_address: "Gratitude and reciprocity"
      - wampum: "Sacred records, not for external use"
      - clan_system: "Respect for traditional governance"
```

### 4.3 Access Control Implementation

```python
class CulturalAccessControl:
    """
    Enforce access controls for indigenous knowledge
    """

    def __init__(self):
        self.restriction_db = RestrictionDatabase()
        self.fpic_registry = FPICRegistry()

    def check_access_allowed(self,
                            knowledge_id: str,
                            use_context: UseContext) -> AccessDecision:
        """
        Check if proposed use is allowed
        """
        knowledge = self.restriction_db.get(knowledge_id)
        fpic = self.fpic_registry.get(knowledge_id)

        # Check if knowledge is forbidden
        if knowledge.restriction_level == RestrictionLevel.FORBIDDEN:
            return AccessDecision(
                allowed=False,
                reason="This knowledge is marked as forbidden",
                appeal_possible=False
            )

        # Check if knowledge is sacred
        if knowledge.restriction_level == RestrictionLevel.SACRED:
            if not fpic or fpic.status != "approved":
                return AccessDecision(
                    allowed=False,
                    reason="Sacred knowledge requires explicit FPIC approval",
                    appeal_possible=True,
                    appeal_process="Contact community representative"
                )

            # Check if use matches approved scope
            if use_context.use_type not in fpic.approved_uses:
                return AccessDecision(
                    allowed=False,
                    reason=f"Use type {use_context.use_type} not in approved scope",
                    appeal_possible=True
                )

        # Check if knowledge is restricted
        if knowledge.restriction_level == RestrictionLevel.RESTRICTED:
            # Check if conditions are met
            if not self.check_conditions(knowledge.conditions, use_context):
                return AccessDecision(
                    allowed=False,
                    reason="Use conditions not met",
                    conditions=knowledge.conditions
                )

        # Check commercial use
        if use_context.commercial and knowledge.restriction_level in [
            RestrictionLevel.ATTRIBUTED,
            RestrictionLevel.RESTRICTED
        ]:
            if not fpic or not fpic.allows_commercial:
                return AccessDecision(
                    allowed=False,
                    reason="Commercial use not approved for this knowledge",
                    appeal_possible=True
                )

        # Check attribution requirements
        if not use_context.includes_attribution:
            return AccessDecision(
                allowed=False,
                reason="Attribution required",
                required_attribution=knowledge.attribution_template
            )

        return AccessDecision(allowed=True)

    def check_conditions(self,
                        conditions: List[Condition],
                        use_context: UseContext) -> bool:
        """
        Check if use context meets conditions
        """
        for condition in conditions:
            if condition.type == "non-commercial":
                if use_context.commercial:
                    return False
            elif condition.type == "educational-only":
                if use_context.use_type != "education":
                    return False
            elif condition.type == "community-review":
                if not use_context.reviewed_by_community:
                    return False
            elif condition.type == "benefit-sharing":
                if not use_context.benefit_sharing_active:
                    return False
            # Additional condition types...

        return True
```

---

## 5. Community Engagement Guide {#community-engagement}

### 5.1 Engagement Principles

```yaml
EngagementPrinciples:
  begin_before_you_need:
    - "Build relationships before requesting anything"
    - "Show up for community needs first"
    - "Demonstrate long-term commitment"

  respect_protocols:
    - "Learn the community's engagement protocols"
    - "Follow proper introduction procedures"
    - "Honor time and relationship requirements"

  capacity_building:
    - "Offer skills and resources to community"
    - "Support community-led initiatives"
    - "Hire and train community members"

  reciprocity:
    - "Give before you take"
    - "Ensure mutual benefit"
    - "Share credit and recognition"

  flexibility:
    - "Adapt to community needs and timelines"
    - "Adjust approaches based on feedback"
    - "Accept that outcomes may differ from expectations"
```

### 5.2 Engagement Process

```
┌─────────────────────────────────────────────────────────────┐
│              COMMUNITY ENGAGEMENT PROCESS                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   PHASE 1: PREPARATION (3-6 months before)                 │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Research community history and context             │  │
│   │ • Identify appropriate representatives              │  │
│   │ • Learn protocols and customs                        │  │
│   │ • Build relationships (show up, give first)          │  │
│   │ • Prepare clear materials in accessible language     │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   PHASE 2: INITIAL OUTREACH                                │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Request meeting through proper channels            │  │
│   │ • Present POLLN and your intentions                  │  │
│   │ • Listen to community priorities                     │  │
│   │ • Adjust approach based on feedback                  │  │
│   │ • Leave materials for community review               │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   PHASE 3: COLLABORATIVE DISCUSSION                       │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Community takes time to discuss internally         │  │
│   │ • Follow up on community timeline (not yours)        │  │
│   │ • Address questions and concerns thoroughly           │  │
│   │ • Co-create approach with community input            │  │
│   │ • Identify community benefits                        │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   PHASE 4: CONSENT DECISION                               │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Community makes decision (yes, no, conditional)    │  │
│   │ • Respect decision regardless of outcome             │  │
│   │ • If yes: Document conditions and requirements       │  │
│   │ • If no: Thank community, maintain relationship      │  │
│   │ • If conditional: Work to meet conditions            │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   PHASE 5: ONGOING RELATIONSHIP                           │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Implement according to agreement                   │  │
│   │ • Regular check-ins and reporting                    │  │
│   │ • Deliver benefits as promised                       │  │
│   │ • Maintain communication channels                    │  │
│   │ • Seek feedback and adjust accordingly               │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Community-Specific Considerations

#### Haudenosaunee (Six Nations)

```yaml
Haudenosaunee:
  key_concepts:
    - great_law_of_peace: "FPIC REQUIRED for detailed use"
    - wampum_belts: "ABSOLUTE RESTRICTION - Do not use"
    - consensus_governance: "Respect decision-making process"
    - thanksgiving_address: "Model of reciprocity"

  engagement_protocols:
    - approach: "Through proper clan mothers or chiefs"
    - decision_making: "Consensus-based, takes time"
    - meeting_format: "Traditional protocols may apply"
    - gifts: "Appropriate to give offerings"

  representatives:
    - "Haudenosaunee Confederacy (traditional governance)"
    - "Elected band councils (may not have authority over TK)"
    - "Cultural centers and knowledge keepers"

  red_flags:
    - "Do not go around traditional leadership"
    - "Do not pressure for quick decisions"
    - "Do not use wampum belt concepts under any circumstances"
```

#### Lakota

```yaml
Lakota:
  key_concepts:
    - mitakuye_oyasin: "FPIC REQUIRED for use"
    - hocoka: "ABSOLUTE RESTRICTION - Do not use"
    - wolakota: "Peace and harmony principles"
    - tiwahe: "Family-centered ethics"

  engagement_protocols:
    - approach: "Through tribal council or traditional knowledge keepers"
    - decision_making: "Elders have authority"
    - timing: "Consider ceremonial calendar"
    - protocols: "Respect for elders and traditions"

  representatives:
    - "Tribal councils (elected governments)"
    - "Traditional knowledge keepers (elders)"
    - "Tribal historic preservation offices"

  red_flags:
    - "Never use ceremonial knowledge"
    - "Respect restrictions on sacred knowledge"
    - "Do not pressure for rapid decisions"
```

#### Māori

```yaml
Maori:
  key_concepts:
    - whakapapa: "FPIC REQUIRED for use"
    - mauri: "FPIC REQUIRED for use"
    - kaitiakitanga: "Stewardship principles"
    - manaakitanga: "Hospitality and care"
    - tikanga: "Cultural protocols"

  engagement_protocols:
    - approach: "Through iwi (tribal) authorities"
    - decision_making: "Iwi authorities have authority"
    - powhiri: "May be appropriate formal welcome"
    - koha: "Gift-giving protocol"

  representatives:
    - "Iwi authorities (tribal governing bodies)"
    - "Māori research ethics boards"
    - "Kaumātua (elders) with appropriate authority"

  red_flags:
    - "Respect kaitiakitanga over knowledge"
    - "Honor tikanga in all interactions"
    - "Do not assume individual speaks for iwi"
```

#### Yoruba

```yaml
Yoruba:
  key_concepts:
    - ase: "Consultation recommended"
    - ori: "Consultation recommended"
    - ifa: "Restricted knowledge - respect protocols"
    - ubuntu_variants: "Community-focused ethics"

  engagement_protocols:
    - approach: "Through traditional authorities or community organizations"
    - decision_making: "May involve traditional authorities"
    - respect: "Show respect for traditions"
    - reciprocity: "Give back to community"

  representatives:
    - "Traditional rulers and chiefs"
    - "Community organizations"
    - "Cultural centers"

  red_flags:
    - "Respect restrictions on Ifa and other specialized knowledge"
    - "Do not treat Yoruba knowledge as monolithic"
    - "Recognize diversity across Yoruba communities"
```

### 5.4 Engagement Timeline

| Phase | Duration | Activities | Key Milestones |
|-------|----------|------------|----------------|
| **Preparation** | 3-6 months | Research, relationship building | Established contact |
| **Initial Outreach** | 1-3 months | First meetings, information sharing | Community understands POLLN |
| **Community Discussion** | 2-6 months | Community internal process | Community ready to decide |
| **Decision** | 1 month | Consent decision | FPIC status determined |
| **Implementation** | Ongoing | Implement according to agreement | Benefits delivered |
| **Maintenance** | Ongoing | Regular communication | Relationships maintained |

**Total Timeline:** 6-18 months for initial FPIC (varies by community)

---

## 6. Technical Implementation Protocol {#technical-implementation}

### 6.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            FPIC TECHNICAL ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   LAYER 1: Knowledge Metadata Registry                     │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Indigenous Knowledge Database                      │  │
│   │ • FPIC Consent Records                              │  │
│   │ • Restriction Classifications                       │  │
│   │ • Attribution Templates                             │  │
│   │ • Benefit Sharing Arrangements                      │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   LAYER 2: Access Control Engine                          │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Restriction Level Enforcement                     │  │
│   │ • Use Context Analysis                              │  │
│   │ • Permission Checking                               │  │
│   │ • Conditional Logic Engine                          │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   LAYER 3: Attribution Injection                          │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Code Comment Injection                            │  │
│   │ • Documentation Attribution                         │  │
│   │ • UI Tooltip/Notice System                          │  │
│   │ • API Response Metadata                             │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   LAYER 4: Monitoring & Reporting                         │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Usage Tracking                                    │  │
│   │ • Benefit Calculation                               │  │
│   │ • Compliance Reporting                              │  │
│   │ • Community Dashboard                               │  │
│   └─────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│   LAYER 5: Governance Interface                           │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ • Community Representative Portal                   │  │
│   │ • FPIC Request/Approval System                      │  │
│   │ • Benefit Distribution Management                   │  │
│   │ • Audit Log & Reporting                             │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Database Schema

```sql
-- Indigenous Knowledge Registry
CREATE TABLE indigenous_knowledge (
    knowledge_id UUID PRIMARY KEY,
    concept_name VARCHAR(255) NOT NULL,
    source_tradition VARCHAR(255) NOT NULL,
    language VARCHAR(100),
    description TEXT,
    cultural_context TEXT,

    -- Classification
    restriction_level VARCHAR(50) NOT NULL,
    sensitivity_score INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),

    CONSTRAINT valid_restriction_level
        CHECK (restriction_level IN ('public', 'attributed', 'restricted', 'sacred', 'forbidden'))
);

-- FPIC Consent Registry
CREATE TABLE fpic_consents (
    consent_id UUID PRIMARY KEY,
    knowledge_id UUID REFERENCES indigenous_knowledge(knowledge_id),

    -- Consent Details
    status VARCHAR(50) NOT NULL,
    requested_at TIMESTAMP NOT NULL,
    decided_at TIMESTAMP,
    decision_valid_until TIMESTAMP,

    -- Community Representation
    community_name VARCHAR(255) NOT NULL,
    representative_name VARCHAR(255) NOT NULL,
    representative_role VARCHAR(255),
    representative_credentials TEXT,

    -- Consent Scope
    approved_uses TEXT[], -- JSON array of approved use types
    conditions TEXT[], -- JSON array of conditions
    benefit_sharing_arrangement TEXT, -- JSON object

    -- Documentation
    consent_document_path VARCHAR(500),
    notes TEXT,

    CONSTRAINT valid_status
        CHECK (status IN ('pending', 'in_review', 'approved', 'restricted', 'denied', 'withdrawn'))
);

-- Knowledge Usage Tracking
CREATE TABLE knowledge_usage (
    usage_id UUID PRIMARY KEY,
    knowledge_id UUID REFERENCES indigenous_knowledge(knowledge_id),
    consent_id UUID REFERENCES fpic_consents(consent_id),

    -- Usage Details
    component_type VARCHAR(100),
    component_name VARCHAR(255),
    feature_name VARCHAR(255),

    -- Context
    use_type VARCHAR(100),
    is_commercial BOOLEAN DEFAULT FALSE,
    includes_attribution BOOLEAN DEFAULT TRUE,

    -- Tracking
    first_used_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP DEFAULT NOW(),
    usage_count INTEGER DEFAULT 0,

    -- Audit
    added_by VARCHAR(255),
    reviewed_by_community BOOLEAN DEFAULT FALSE
);

-- Benefit Sharing Registry
CREATE TABLE benefit_sharing (
    benefit_id UUID PRIMARY KEY,
    knowledge_id UUID REFERENCES indigenous_knowledge(knowledge_id),
    consent_id UUID REFERENCES fpic_consents(consent_id),

    -- Benefit Details
    benefit_type VARCHAR(100), -- financial, capacity_building, etc.
    amount DECIMAL(10,2),
    currency VARCHAR(10),

    -- Distribution
    community_fund VARCHAR(255),
    distribution_schedule VARCHAR(100),
    last_distributed_at TIMESTAMP,
    next_distribution_due_at TIMESTAMP,

    -- Documentation
    arrangement_document_path VARCHAR(500),
    notes TEXT
);

-- Attribution Templates
CREATE TABLE attribution_templates (
    template_id UUID PRIMARY KEY,
    knowledge_id UUID REFERENCES indigenous_knowledge(knowledge_id),

    -- Template Content
    template_type VARCHAR(100), -- code, docs, ui, api
    template_text TEXT NOT NULL,

    -- Variables
    variables JSONB, -- Variable names and descriptions

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    approved_by_community BOOLEAN DEFAULT FALSE
);

-- Audit Log
CREATE TABLE fpic_audit_log (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    knowledge_id UUID REFERENCES indigenous_knowledge(knowledge_id),

    -- Event Details
    event_data JSONB,
    performed_by VARCHAR(255),
    performed_at TIMESTAMP DEFAULT NOW(),

    -- Context
    component_affected VARCHAR(255),
    ip_address INET,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_knowledge_tradition ON indigenous_knowledge(source_tradition);
CREATE INDEX idx_knowledge_restriction ON indigenous_knowledge(restriction_level);
CREATE INDEX idx_consent_status ON fpic_consents(status);
CREATE INDEX idx_consent_knowledge ON fpic_consents(knowledge_id);
CREATE INDEX idx_usage_knowledge ON knowledge_usage(knowledge_id);
CREATE INDEX idx_audit_knowledge ON fpic_audit_log(knowledge_id);
CREATE INDEX idx_audit_date ON fpic_audit_log(performed_at);
```

### 6.3 API Interface

```typescript
/**
 * FPIC Service API Interface
 */

interface FPICService {
  // Knowledge Registry
  registerKnowledge(knowledge: IndigenousKnowledge): Promise<KnowledgeID>;
  getKnowledge(knowledgeId: KnowledgeID): Promise<IndigenousKnowledge>;
  searchKnowledge(criteria: SearchCriteria): Promise<IndigenousKnowledge[]>;
  updateKnowledge(knowledgeId: KnowledgeID, updates: KnowledgeUpdate): Promise<void>;

  // FPIC Consent Management
  requestConsent(request: ConsentRequest): Promise<ConsentRequestID>;
  getConsentStatus(consentId: ConsentRequestID): Promise<ConsentStatus>;
  recordDecision(consentId: ConsentRequestID, decision: ConsentDecision): Promise<void>;
  checkConsent(knowledgeId: KnowledgeID, useContext: UseContext): Promise<ConsentCheck>;

  // Access Control
  checkAccessAllowed(knowledgeId: KnowledgeID, useContext: UseContext): Promise<AccessDecision>;
  validateUsage(component: Component, knowledgeIds: KnowledgeID[]): Promise<ValidationResult>;

  // Attribution
  getAttributionTemplate(knowledgeId: KnowledgeID, templateType: TemplateType): Promise<AttributionTemplate>;
  generateAttribution(knowledgeIds: KnowledgeID[], format: AttributionFormat): Promise<string>;
  injectAttribution(content: string, knowledgeIds: KnowledgeID[], format: Format): Promise<string>;

  // Usage Tracking
  recordUsage(usage: KnowledgeUsage): Promise<void>;
  getUsageReport(knowledgeId: KnowledgeID, period: DateRange): Promise<UsageReport>;

  // Benefit Sharing
  calculateBenefit(usageId: UsageID): Promise<BenefitShare>;
  recordBenefitDistribution(benefit: BenefitDistribution): Promise<void>;
  getBenefitReport(knowledgeId: KnowledgeID, period: DateRange): Promise<BenefitReport>;

  // Community Interface
  createCommunityPortal(communityId: CommunityID): Promise<PortalAccess>;
  getCommunityDashboard(communityId: CommunityID): Promise<CommunityDashboard>;
  submitCommunityFeedback(feedback: CommunityFeedback): Promise<void>;
}

// Type Definitions
type ConsentStatus = 'pending' | 'in_review' | 'approved' | 'restricted' | 'denied' | 'withdrawn';
type RestrictionLevel = 'public' | 'attributed' | 'restricted' | 'sacred' | 'forbidden';
type TemplateType = 'code' | 'docs' | 'ui' | 'api';
type AttributionFormat = 'markdown' | 'html' | 'plain' | 'json';

interface ConsentCheck {
  hasConsent: boolean;
  consentStatus?: ConsentStatus;
  conditions?: Condition[];
  expiresAt?: Date;
  appealProcess?: string;
}

interface AccessDecision {
  allowed: boolean;
  reason?: string;
  conditions?: Condition[];
  appealPossible?: boolean;
  appealProcess?: string;
  requiredAttribution?: string;
}

interface UseContext {
  useType: string;
  isCommercial: boolean;
  includesAttribution: boolean;
  reviewedByCommunity: boolean;
  benefitSharingActive: boolean;
  additionalContext?: Record<string, any>;
}

interface Condition {
  type: string;
  description: string;
  satisfied: boolean;
  howToSatisfy?: string;
}
```

### 6.4 Integration Points

```yaml
IntegrationPoints:
  code_base:
    - pre_commit_hooks: "Check for indigenous knowledge usage"
    - ci_pipeline: "Validate FPIC status for all code"
    - code_review: "Require FPIC approval for indigenous concepts"
    - documentation: "Auto-inject attribution comments"

  documentation:
    - build_process: "Inject attribution into docs"
    - api_docs: "Include TK labels in API documentation"
    - readme: "Add indigenous knowledge section"
    - website: "Public attribution page"

  marketplace:
    - listing_creation: "Check for indigenous knowledge"
    - pricing: "Calculate benefit sharing amount"
    - distribution: "Route benefits to community funds"
    - reporting: "Track sales and report to communities"

  development_tools:
    - ide_extension: "Show FPIC status in editor"
    - cli_command: "Check knowledge status"
    - documentation_generator: "Auto-generate attribution"
    - testing: "Validate access controls"
```

---

## 7. Case Studies: Lessons Learned {#case-studies}

### 7.1 Successful FPIC Implementations

#### Case Study: Te Mana Raraunga (Māori Data Sovereignty)

**Context:** Māori data sovereignty network in New Zealand

**What Worked:**
- Māori-led governance from the start
- Clear framework for data classification
- Partnership model with government agencies
- Capacity building alongside policy development

**Key Lessons:**
1. Indigenous governance is non-negotiable
2. Build capacity while building systems
3. Partnerships must be equitable, not extractive
4. Cultural protocols can be operationalized in technical systems

**Applicable to POLLN:**
- Māori partnership for whakapapa and mauri concepts
- Data classification framework for restriction levels
- Partnership model for governance council

#### Case Study: First Nations Information Governance Centre (Canada)

**Context:** First Nations data governance in Canada

**What Worked:**
- OCAP principles (Ownership, Control, Access, Possession)
- Community-driven data standards
- Capacity building through training
- Sustainable funding model

**Key Lessons:**
1. Principles must be operationalized
2. Communities need tools to exercise sovereignty
3. Training is essential for capacity
4. Sustainable resourcing is critical

**Applicable to POLLN:**
- OCAP-inspired access control framework
- Community portal for self-service governance
- Training programs for indigenous technologists

#### Case Study: Local Contexts TK Labels

**Context:** Traditional Knowledge Labels initiative

**What Worked:**
- Flexible, community-defined labels
- Integration with existing systems (museums, archives)
- Respect for cultural protocols
- Practical technical implementation

**Key Lessons:**
1. Labels must be community-defined, not imposed
2. Integration with existing systems increases adoption
3. Technical systems must respect cultural constraints
4. Simplicity enables widespread use

**Applicable to POLLN:**
- TK Labels for knowledge classification
- Integration into existing developer workflows
- Community portal for label management

### 7.2 Failures and Cautionary Tales

#### Failure: Genetic Research with Havasupai Tribe

**Context:** Researchers used blood samples for purposes beyond consent

**What Happened:**
- Tribe consented to diabetes research
- Samples were used for schizophrenia research, migration studies, and inbreeding
- Violated cultural beliefs about blood
- Tribe sued and won settlement

**Key Failures:**
1. Broad consent without specific use limitations
2. Failure to respect cultural context
3. No ongoing relationship or consultation
4. Assumed consent could be expanded

**Lessons for POLLN:**
- Consent must be specific about use cases
- Cultural context matters for all knowledge
- Ongoing relationship is essential
- Consent cannot be expanded without new FPIC

#### Failure: Maasai Image Rights

**Context:** Maasai image used commercially without compensation

**What Happened:**
- Maasai warriors' images used for marketing
- No compensation to community
- Cultural symbols appropriated
- Community received no benefit

**Key Failures:**
1. No FPIC obtained
2. No benefit sharing
3. Cultural appropriation for commercial gain
4. No community control

**Lessons for POLLN:**
- Explicit FPIC required for all indigenous knowledge
- Benefit sharing must be structured upfront
- Commercial use requires specific approval
- Communities must control how their knowledge is used

#### Failure: Indigenous Knowledge Digitization Projects

**Context:** Multiple digitization projects that failed

**Common Issues:**
- Digitized without consent
- Put knowledge online without restrictions
- Violated cultural protocols around access
- No benefit to communities

**Key Failures:**
1. Western assumptions about "open knowledge"
2. Failure to understand cultural restrictions
3. No community control over digitized materials
4. Extraction without reciprocity

**Lessons for POLLN:**
- Not all knowledge should be "open"
- Access controls are technically necessary
- Community control is essential
- Reciprocity is mandatory

### 7.3 Emerging Best Practices

#### Practice 1: Start with Relationships, Not Projects

```yaml
RelationshipFirst:
  wrong_approach:
    - "We have a project, will you help us?"
    - "We need your knowledge for X"
    - "Can you approve this quickly?"

  right_approach:
    - "We want to build a relationship"
    - "How can we support your community?"
    - "What are your priorities?"
    - "Eventually, we'd like to discuss potential collaboration"
```

#### Practice 2: Indigenous Governance from Day One

```yaml
IndigenousGovernance:
  principle: "Nothing about us without us"

  implementation:
    - indigenous_council: "Real veto power from day one"
    - co_design: "Indigenous voices in system design"
    - decision_making: "Indigenous representatives make decisions"
    - compensation: "Fair compensation for time and expertise"
```

#### Practice 3: Capacity Building as a Core Outcome

```yaml
CapacityBuilding:
  principle: "Build community capacity alongside technology"

  implementation:
    - training: "Train indigenous technologists"
    - tools: "Provide tools to communities"
    - infrastructure: "Support community-owned infrastructure"
    - careers: "Hire indigenous professionals"
```

#### Practice 4: Sustainable Long-Term Engagement

```yaml
SustainableEngagement:
  principle: "FPIC is not a one-time event"

  implementation:
    - ongoing_communication: "Regular check-ins, not just when needed"
    - long_term_funding: "Fund community partnerships long-term"
    - adaptive_approach: "Adjust based on community feedback"
    - exit_strategy: "Plan for long-term sustainability"
```

---

## 8. Compliance Checklist {#compliance-checklist}

### 8.1 Pre-Use Checklist

Before using any indigenous knowledge in POLLN, complete this checklist:

```markdown
## Indigenous Knowledge Use Checklist

### Identification
- [ ] Knowledge source identified (tradition, community, language)
- [ ] Cultural context researched and documented
- [ ] Traditional owners/keepers identified
- [ ] Knowledge classification completed (restriction level)

### FPIC Status
- [ ] FPIC status verified (approved/restricted/denied/pending)
- [ ] Consent record located and reviewed
- [ ] Consent scope checked against proposed use
- [ ] Consent expiration date checked (if applicable)
- [ ] Consent conditions documented and understood

### Cultural Appropriateness
- [ ] Cultural sensitivity assessment completed
- [ ] Community representatives consulted (if required)
- [ ] Cultural protocols respected
- [ ] Sacred/restricted knowledge identified and excluded

### Attribution
- [ ] Attribution statement prepared
- [ ] Attribution placement determined
- [ ] Attribution approved by community (if required)
- [ ] Community feedback on attribution incorporated

### Access Control
- [ ] Restriction level enforced in code
- [ ] Access control checks implemented
- [ ] Conditional use requirements met
- [ ] Commercial use authorization verified (if applicable)

### Benefit Sharing
- [ ] Benefit sharing arrangement activated
- [ ] Benefits calculated and documented
- [ ] Benefit distribution mechanism activated
- [ ] Community informed of benefits

### Documentation
- [ ] Knowledge metadata updated
- [ ] Usage recorded in tracking system
- [ ] Attribution injected into code/docs
- [ ] FPIC reference documented

### Review & Approval
- [ ] Indigenous Liaison review completed
- [ ] Governance Council approval (if required)
- [ ] Compliance verification completed
- [ ] Sign-off obtained
```

### 8.2 Continuous Compliance Checklist

```markdown
## Ongoing Compliance Checklist

### Quarterly Review
- [ ] Review all indigenous knowledge use in system
- [ ] Verify consent status still current
- [ ] Check for new community concerns
- [ ] Update knowledge metadata if needed
- [ ] Review benefit distribution
- [ ] Community check-in completed

### Annual Review
- [ ] Comprehensive audit of indigenous knowledge use
- [ ] Community feedback solicited
- [ ] FPIC consent renewal/review
- [ ] Benefit sharing assessment
- [ ] Cultural impact assessment
- [ ] Public report prepared

### Trigger Events
- [ ] New feature using indigenous knowledge → FPIC review
- [ ] Change in commercial status → Benefit review
- [ ] Community concern raised → Immediate review
- [ ] New research/knowledge about concept → Context review
- [ ] System architecture change → Impact assessment
```

### 8.3 Release Checklist

```markdown
## Release Compliance Checklist

### Pre-Release
- [ ] All indigenous knowledge identified in release
- [ ] FPIC consent verified for all new knowledge
- [ ] Attribution statements reviewed
- [ ] Access controls verified
- [ ] Benefit sharing calculated
- [ ] Documentation updated
- [ ] Indigenous Liaison sign-off obtained
- [ ] Governance Council approval (if required)

### Release Notes
- [ ] Indigenous knowledge properly credited
- [ ] Cultural context provided
- [ ] FPIC acknowledgments included
- [ ] Community partnerships acknowledged

### Post-Release
- [ ] Community representatives notified
- [ ] Usage monitoring activated
- [ ] Benefit distribution scheduled
- [ ] Feedback mechanisms activated
```

---

## 9. Templates & Resources {#templates}

### 9.1 FPIC Request Template

```markdown
## FPIC Request Form

**Date:** [DATE]
**Request ID:** [UNIQUE ID]
**POLLN Project:** [SuperInstance/POLLN]

### Requester Information

**Name:** [YOUR NAME]
**Role:** [YOUR ROLE]
**Organization:** [SuperInstance]
**Contact:** [EMAIL]
**Affiliation:** [IF APPLICABLE]

### Knowledge Information

**Concept Name:** [CONCEPT]
**Source Tradition:** [TRADITION/COMMUNITY]
**Language:** [LANGUAGE]
**Description:** [DESCRIBE THE CONCEPT]

**Cultural Context:** [WHAT YOU KNOW ABOUT THE CULTURAL CONTEXT]

**Current Understanding:** [DESCRIBE YOUR UNDERSTANDING OF THE CONCEPT]

### Proposed Use

**Component/Feature:** [WHERE IT WILL BE USED]
**Use Case:** [DESCRIBE THE USE CASE]
**Technical Implementation:** [HOW IT WILL BE IMPLEMENTED]
**Documentation:** [HOW IT WILL BE DOCUMENTED]

### Usage Scope

**Is Commercial Use Intended?** [YES/NO]
**If Yes, Please Describe:** [COMMERCIAL USE DETAILS]

**Will Knowledge Be Modified?** [YES/NO]
**If Yes, Please Describe:** [NATURE OF MODIFICATIONS]

**Will Knowledge Be Combined With Other Knowledge?** [YES/NO]
**If Yes, Please Describe:** [OTHER KNOWLEDGE SOURCES]

### Commitments

**Attribution:** [HOW WE WILL ATTRIBUTE THE KNOWLEDGE]

**Benefit Sharing:** [HOW WE WILL SHARE BENEFITS]

**Community Control:** [HOW COMMUNITY WILL MAINTAIN CONTROL]

**Ongoing Relationship:** [HOW WE WILL MAINTAIN RELATIONSHIP]

### Request

**We are requesting:** [DESCRIBE WHAT YOU'RE REQUESTING - PERMISSION, PARTNERSHIP, GUIDANCE, ETC.]

**Timeline:** [YOUR TIMELINE - BUT RECOGNIZE COMMUNITY TIMELINE]

**Questions for Community:** [QUESTIONS YOU HAVE]

### Supporting Materials

**Attached:** [LIST ATTACHED MATERIALS - TECHNICAL DOCS, DIAGRAMS, ETC.]

### Next Steps

**We hope to:** [YOUR HOPES - MEETING, CONVERSATION, PARTNERSHIP]

**Contact for Follow-up:** [CONTACT INFORMATION]

---

**Thank you for considering this request. We respect your decision whatever it may be, and we honor your stewardship of this knowledge.**
```

### 9.2 Community Meeting Agenda Template

```markdown
## Community Meeting Agenda: POLLN Indigenous Knowledge Partnership

**Date:** [DATE]
**Time:** [TIME]
**Location:** [LOCATION/ZOOM LINK]
**Host Community:** [COMMUNITY NAME]
**POLLN Representatives:** [NAMES]

### Opening (TIME)

**Welcome and Introductions**
- Welcome from community representative
- Introduction of POLLN representatives
- Opening remarks/ceremony if appropriate

### Background (TIME)

**POLLN Project Overview**
- What is POLLN?
- Why are we here?
- Our interest in [COMMUNITY] knowledge

**Our Commitments**
- Respect for cultural protocols
- Community control over knowledge
- Benefit sharing
- Long-term relationship

### Discussion (TIME)

**[SPECIFIC CONCEPT] Knowledge**
- Our understanding of the concept
- How we hope to use it
- Questions for community

**Community Concerns**
- What concerns does the community have?
- What conditions would need to be met?
- What benefits would the community like?

**Next Steps**
- Community discussion process
- Timeline for decision
- Follow-up communication

### Closing (TIME)

**Summary**
- Key points discussed
- Agreed next steps
- Contact information

**Closing**
- Thank you
- Closing ceremony if appropriate

### Logistics

**Before Meeting**
- [ ] Send materials in advance
- [ ] Confirm attendance
- [ ] Prepare presentation
- [ ] Bring any offerings/gifts if appropriate

**After Meeting**
- [ ] Send thank you note
- [ ] Distribute meeting notes for approval
- [ ] Follow up on action items
- [ ] Honor agreed timeline
```

### 9.3 Attribution Statement Generator

```python
class AttributionGenerator:
    """
    Generate attribution statements for indigenous knowledge
    """

    def generate_attribution(self,
                           knowledge_id: str,
                           context: str) -> str:
        """
        Generate appropriate attribution for context
        """
        knowledge = self.get_knowledge(knowledge_id)
        fpic = self.get_fpic_status(knowledge_id)

        if context == "code":
            return self._code_attribution(knowledge, fpic)
        elif context == "documentation":
            return self._docs_attribution(knowledge, fpic)
        elif context == "ui":
            return self._ui_attribution(knowledge, fpic)
        elif context == "api":
            return self._api_attribution(knowledge, fpic)

    def _code_attribution(self, knowledge, fpic):
        return f"""
# Indigenous Knowledge Attribution

# This code incorporates concepts from {knowledge.source_tradition} knowledge systems.

# Concept: {knowledge.concept_name}
# Tradition: {knowledge.source_tradition}
# Language: {knowledge.language}

# Used with permission from {knowledge.community_name}
# FPIC Status: {fpic.status} (dated {fpic.decided_at})
# Approved by: {fpic.representative_name}

# For full attribution details, see: [LINK TO FULL ATTRIBUTION]
"""

    def _docs_attribution(self, knowledge, fpic):
        return f"""
## Indigenous Knowledge Attribution

This documentation incorporates the concept of **{knowledge.concept_name}**,
which originates from {knowledge.source_tradition} knowledge systems.

### Source Recognition

{knowledge.concept_name} is traditional knowledge that has been stewarded by
the {knowledge.community_name} for {knowledge.time_period}. This knowledge
comes from {knowledge.cultural_context}.

### Use Permission

This use has been approved under FPIC protocol dated {fpic.decided_at}.
The {fpic.representative_name} granted permission on behalf of
{fpic.community_name}.

**Approved Uses:** {', '.join(fpic.approved_uses)}
**Conditions:** {', '.join(fpic.conditions) if fpic.conditions else 'None'}

### Our Commitments

We are committed to:
- Respecting the full cultural context of this knowledge
- Honoring any restrictions or conditions on its use
- Sharing benefits with the {knowledge.community_name}
- Ongoing consultation with community representatives
- Immediate cessation of use if requested

### Learn More

- Full FPIC documentation: [LINK]
- Community resources: [LINK IF APPLICABLE]
- Contact for concerns: [EMAIL]
"""

    def _ui_attribution(self, knowledge, fpic):
        # Short, subtle attribution for UI
        # Shown on hover or in footer
        return f"Incorporates {knowledge.concept_name} from {knowledge.source_tradition} knowledge systems. Used with permission. Learn more: [LINK]"

    def _api_attribution(self, knowledge, fpic):
        # Metadata for API responses
        return {
            "indigenous_knowledge": [
                {
                    "concept": knowledge.concept_name,
                    "tradition": knowledge.source_tradition,
                    "community": knowledge.community_name,
                    "fpic_status": fpic.status,
                    "attribution_link": "[LINK TO FULL ATTRIBUTION]"
                }
            ]
        }
```

### 9.4 Community Resources

```yaml
CommunityResources:
  organizations:
    indigenous_data_governance:
      - name: "Global Indigenous Data Alliance (GIDA)"
        focus: "Indigenous data governance principles"
        url: "https://gidalliance.org"

      - name: "Local Contexts"
        focus: "Traditional Knowledge Labels"
        url: "https://localcontexts.org"

      - name: "First Nations Information Governance Centre (FNIGC)"
        focus: "First Nations data sovereignty in Canada"
        url: "https://fnigc.ca"

      - name: "Te Mana Raraunga"
        focus: "Māori data sovereignty"
        url: "https://temanararaunga.maori.nz"

  frameworks:
    - name: "CARE Principles for Indigenous Data Governance"
      description: "Collective Benefit, Authority, Responsibility, Ethics"
      url: "https://www.gida-global.org/care"

    - name: "UN Declaration on the Rights of Indigenous Peoples (UNDRIP)"
      description: "International standard for indigenous rights"
      url: "https://www.un.org/development/desa/indigenouspeoples/declaration-on-the-rights-of-indigenous-peoples.html"

    - name: "OCAP Principles"
      description: "Ownership, Control, Access, Possession"
      context: "First Nations data sovereignty"

    - name: "Mataatua Declaration"
      description: "Cultural and intellectual property rights of indigenous peoples"
      url: "https://archive.iucn.org/topics/health/biodiversityhr/Mataatua.pdf"

  reading:
    fpic:
      - title: "Free, Prior and Informed Consent: A Human Rights Approach"
        author: "Tebtebba Foundation"
        url: "https://www.tebtebba.org"

      - title: "FPIC: A Right, Not a Principle"
        author: "International Work Group for Indigenous Affairs"
        url: "https://www.iwgia.org"

    indigenous_data:
      - title: "Indigenous Data Sovereignty and Policy"
        editors: "Rainie, Kukutai, Walter"
        publisher: "ANU Press"
        year: 2019

      - title: "CARE Principles for Indigenous Data Governance"
        author: "Global Indigenous Data Alliance"
        year: 2019

    case_studies:
      - title: "Data Sovereignty and Indigenous Knowledge Governance"
        journal: "AI & Society"
        year: 2020

      - title: "Traditional Knowledge Labels: An Indigenous Approach"
        conference: "Museums and the Web"
        year: 2018

  training:
    - name: "Indigenous Data Sovereignty Course"
        provider: "Mukurtu CMS"
        url: "https://mukurtu.org"

      - name: "Working with Indigenous Communities"
        provider: "Local Contexts"
        url: "https://localcontexts.org"

      - name: "FPIC Implementation Training"
        provider: "Various community organizations"
        recommendation: "Seek community-led training"
```

---

## Conclusion

### Key Takeaways

1. **FPIC is Non-Negotiable**: Free, Prior, and Informed Consent is the minimum standard for engaging with indigenous knowledge. It's not optional.

2. **Relationships Over Transactions**: FPIC is about building ongoing relationships, not obtaining one-time permissions.

3. **Community Control is Essential**: Indigenous communities must have actual control over their knowledge, including veto power.

4. **Benefit Sharing is Mandatory**: If POLLN benefits from indigenous knowledge, communities must share in those benefits.

5. **Technical Systems Must Reflect Ethics**: Access controls, attribution, and benefit sharing must be built into the technical architecture.

6. **Continuous Engagement**: FPIC is not a one-time event - it requires ongoing relationship and communication.

7. **Humility and Respect**: Approach indigenous knowledge with humility, recognizing that you are a guest in these knowledge systems.

### Implementation Priority

1. **Immediate**: Implement access controls and tracking systems
2. **Short-term**: Begin community engagement for priority concepts
3. **Medium-term**: Obtain FPIC for core concepts
4. **Long-term**: Build sustainable partnerships and benefit sharing

### Next Steps

1. **Review this document** with the POLLN team
2. **Identify all indigenous concepts** currently used
3. **Audit current FPIC status** for each concept
4. **Prioritize community engagement** based on use and sensitivity
5. **Begin relationship building** with priority communities
6. **Implement technical controls** for access and attribution
7. **Establish benefit sharing** mechanisms
8. **Create Indigenous Governance Council** with actual veto power

---

**Remember**: The goal is not just to avoid harm, but to actively support indigenous sovereignty and wellbeing. When in doubt, the conservative choice is no use.

---

**Document Status**: Active Protocol
**Version**: 1.0
**Last Updated**: 2026-03-06
**Next Review**: 2026-06-06 or after indigenous consultation
**Maintained By**: FPIC Implementation Specialist (Round 2)

**Questions or Concerns**: Contact the Indigenous Liaison Specialist
