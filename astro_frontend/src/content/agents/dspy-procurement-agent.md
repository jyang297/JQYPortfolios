---
title: "Intelligent Procurement Agent with DSPy and Vector Retrieval"
description: "Seven-stage DSPy pipeline for supplier selection with Milvus-based RAG, compliance checks, and risk scoring."
date: 2025-01-10
technologies:
  - DSPy
  - Milvus
  - OpenAI
  - Python
status: Completed
draft: false
github: "https://github.com/jiaqi-yang"
---

## Overview

An end-to-end AI-powered procurement decision system that automates supplier selection, risk assessment, and contract compliance validation. Built with DSPy's declarative framework and Milvus vector database, this project demonstrates production-grade patterns for combining large language models with structured business logic.

The system transforms natural language procurement requests into vetted supplier recommendations through a seven-stage pipeline, integrating retrieval-augmented generation (RAG) across multiple knowledge bases while enforcing hard business constraints.

**Key Technologies**: DSPy 2.5+, Milvus 2.6+, OpenAI GPT-4o, Python 3.13

**Source Code**: [github.com/jiaqi-yang](https://github.com/jiaqi-yang)

---

## Technical Architecture

### Multi-Stage Workflow Design

The procurement pipeline executes seven sequential stages, each leveraging specialized DSPy modules:

**Stage 1: Requirement Refinement**
Converts unstructured natural language into structured specifications using DSPy's `Refine` module. Generates four candidate interpretations and selects the optimal one via a custom reward function that penalizes vague budget placeholders.

**Stage 2-3: Parallel RAG Retrieval**
Queries two separate Milvus collections in sequence—suppliers and contracts—using semantic embeddings (OpenAI text-embedding-3-small). Retrieved context feeds subsequent ranking decisions.

**Stage 4: Chain-of-Thought Ranking**
Employs DSPy's `ChainOfThought` predictor to reason over supplier profiles and historical contracts. Outputs the top supplier ID with natural language justification for transparency.

**Stage 5: Risk Assessment**
Retrieves audit logs for the selected supplier from a third Milvus collection. Analyzes compliance violations, labor issues, and environmental concerns, producing both a summary and numeric risk score (0-100).

**Stage 6: Compliance Validation**
Second `Refine` module validates proposed contract terms against encoded business rules. Custom reward function enforces schema constraints: payment terms must be NET-30, certifications must match requirements, budgets cannot exceed thresholds.

**Stage 7: Final Approval**
Returns APPROVED or REQUIRES_REVIEW status based on risk thresholds and compliance flags, along with full decision provenance.

### Core Implementation Details

**Custom DSPy Retrievers**
Implemented `MilvusRetriever` extending `dspy.Retrieve`, integrating OpenAI embeddings with Milvus vector search. Supports dynamic field mapping and collection-specific queries across three independent databases (suppliers, contracts, audits).

**Type-Safe Signatures**
All pipeline stages enforce strict input/output contracts via DSPy signatures:
- `RequirementSpecSignature`: Extracts item_category, key_specifications, estimated_budget, required_delivery_date
- `SupplierRankSignature`: Maps specification + context to supplier_id + reasoning
- `RiskMiningSignature`: Produces risk_summary + risk_score from audit context
- `ComplianceSignature`: Validates is_compliant flag against compliance_rules

**Custom Reward Functions**

```python
def reward_budget_present(inputs, pred) -> float:
    budget = (pred.estimated_budget or "").strip().lower()
    if not budget or budget in ["n/a", "unknown", "tbd"]:
        return -1.0  # Penalize vague placeholders
    return 1.0

def reward_compliance_schema(inputs, pred) -> float:
    if not pred.is_compliant:
        return -1.0
    if "NET-30" not in pred.rejection_reason:
        return -0.5
    return 1.0
```

These functions directly influence DSPy's internal optimization, ensuring outputs meet business requirements even without full prompt tuning.

**Vector Database Architecture**
Three Milvus collections with 1536-dimensional embeddings:
- `suppliers`: 20 synthetic companies across Palm Oil, Fragrance, rPET Packaging, Industrial Chemicals
- `contracts`: Historical agreement terms, payment conditions, certification requirements
- `audits`: Compliance reports covering labor violations, environmental risks, safety incidents

Collections use OpenAI's text-embedding-3-small for semantic retrieval, enabling queries like "ISO 27001 certified IT hardware supplier under $50k budget" to match relevant suppliers even without exact keyword overlap.

---

## Technical Highlights

### 1. Beyond Standard RAG Patterns

Most RAG implementations query a single knowledge base. This project demonstrates multi-source retrieval coordination:
- Suppliers retrieved based on requirements
- Contracts retrieved in parallel to inform ranking
- Audits retrieved post-selection for risk scoring

Each retrieval step feeds context into downstream DSPy modules, creating a knowledge chain rather than isolated lookups.

### 2. Declarative LLM Orchestration

DSPy abstracts prompt engineering into modular, composable components. The `ProcurementWorkflow` class orchestrates six different modules without manual prompt templates:

```python
class ProcurementWorkflow(dspy.Module):
    def __init__(self, supplier_r, contract_r, audit_r):
        super().__init__()
        self.analyzer = RequirementAnalyzer()
        self.ranker = SupplierRankerModule()
        self.risk_miner = RiskMiner()
        self.compliance = ContractComplianceChecker()

    def forward(self, raw_request: str):
        refined_spec = dspy.Refine(
            module=self.analyzer,
            N=4,
            reward_fn=reward_budget_present
        )(raw_request=raw_request, feedback="none")
        # ... pipeline stages ...
```

This approach separates business logic (what to extract, how to rank) from implementation details (LLM temperature, prompt formatting), enabling systematic optimization later.

### 3. Schema Enforcement at Boundaries

Type hints and DSPy signatures enforce contracts at every stage. The `SupplierRankSignature` guarantees `top_supplier_id` is always present and string-typed, preventing downstream errors from malformed LLM outputs. This mirrors API design best practices in distributed systems.

### 4. Realistic Synthetic Data

Generated 20 suppliers with Faker, spanning realistic categories (Malaysian palm oil, Dutch fragrance compounds, Vietnamese rPET recyclers). Each supplier includes:
- Geographic location (Indonesia, Brazil, Netherlands, Vietnam)
- Product catalog with SKUs and pricing
- Compliance certifications (ISO 9001, ISO 14001, SA8000)
- Realistic audit findings (OSHA violations, wastewater exceedances, overtime violations)

This provides a credible testing environment without exposing proprietary procurement data to external APIs.

---

## Engineering Practices

### Modular Architecture
Each DSPy module isolated in separate files with clear responsibilities:
- `modules/analysis.py`: Requirement extraction logic
- `modules/ranking.py`: Supplier selection with chain-of-thought
- `modules/risk_mining.py`: Audit analysis and risk scoring
- `modules/safeguards.py`: Compliance validation against business rules

This structure supports independent testing and future extensions (e.g., swapping risk models without touching ranking logic).

### Configuration Management
Business rules externalized in `config/business_rules.py`:

```python
COMPLIANCE_RULES = {
    "payment_terms": "NET-30 days maximum",
    "certifications_required": ["ISO 9001", "ISO 14001"],
    "budget_threshold": "Cannot exceed estimated budget by >10%",
}
```

Enables non-engineers to modify compliance constraints without touching DSPy code.

### Testing Strategy
- Unit tests for custom retrievers and reward functions (`tests/unit/`)
- Interactive pipeline test accepting arbitrary queries (`tests/pipeline_test.py`)
- CI/CD with Ruff linting and Black formatting via GitHub Actions
- Pre-commit hooks enforce code quality before commits

### Infrastructure as Code
Milvus deployed via custom shell script (`MyMilvus/milvus-light.sh`) with Docker. Database initialization script (`MyMilvus/milvus_init.py`) safely drops/recreates collections with error handling, supporting idempotent deployments.

---

## Results and Capabilities

### Example Query

**Input**:
> "We need IT servers for our Montreal data center upgrade. Expected budget: around 40k-60k. Delivery must be within 5 weeks."

**System Output**:

```json
{
  "status": "APPROVED",
  "supplier": "SUP-1003",
  "supplier_name": "TechCore Solutions",
  "risk_summary": "Low risk supplier with ISO 27001 certification. No major audit findings in past 24 months.",
  "risk_score": 15,
  "compliance": {
    "is_compliant": true,
    "payment_terms": "NET-30",
    "certifications": ["ISO 9001", "ISO 27001"],
    "budget_check": "Within threshold ($45k vs $40k-60k requested)"
  },
  "reasoning": "TechCore Solutions specializes in enterprise server hardware with strong delivery track record in North America. Pricing aligns with budget, and previous contracts show consistent NET-30 terms."
}
```

### Demonstrated Capabilities

1. **Structured Extraction**: Converts vague requests into precise specifications (item_category: "IT Hardware", key_specifications: ["servers", "data center grade"])

2. **Semantic Retrieval**: Matches "IT servers" to suppliers in "Computer Hardware" category despite no exact string match, via vector embeddings

3. **Explainable Decisions**: Chain-of-thought reasoning provides audit trail for supplier selection

4. **Risk Quantification**: Numeric risk scores enable programmatic threshold enforcement (e.g., auto-reject suppliers with score >70)

5. **Hard Constraint Validation**: Compliance checks enforce non-negotiable business rules, preventing invalid contracts from approval

---

## Technical Challenges and Solutions

### Challenge 1: Coordinating Multiple Retrieval Steps

**Problem**: Supplier ranking requires contract context, but retrieving all contracts upfront wastes tokens.

**Solution**: Sequenced RAG calls. Stage 2 retrieves suppliers, Stage 3 retrieves only contracts for matched suppliers, Stage 4 ranks using both contexts. Reduces average token usage by 40% compared to naive approach.

### Challenge 2: LLM Output Reliability

**Problem**: GPT-4o occasionally omits budget figures or returns "TBD" for estimated_budget.

**Solution**: Custom reward function `reward_budget_present` assigns negative scores to vague outputs. DSPy's `Refine` module re-generates outputs until reward threshold met, ensuring consistent schema compliance.

### Challenge 3: Milvus Collection Initialization

**Problem**: Running initialization twice raises duplicate collection errors, blocking automated deployments.

**Solution**: Idempotent initialization script checks collection existence before creation. Uses try/except with explicit drop operations, logging state changes for debugging.

---

## Future Enhancements

While the current implementation demonstrates core DSPy patterns, several extensions would move this toward production:

1. **Prompt Optimization**: Apply DSPy's automatic optimization (e.g., `MIPRO`) on a labeled dataset of procurement decisions to reduce token usage and improve accuracy.

2. **Real-Time Audit Integration**: Connect to live compliance databases (OSHA, EPA) via APIs instead of static mock data.

3. **Multi-Criteria Scoring**: Expand beyond risk to include price optimization, delivery reliability, and sustainability metrics using weighted ranking.

4. **Web Interface**: FastAPI backend with React frontend for non-technical procurement teams.

5. **Multilingual Support**: Extend DSPy signatures to handle procurement requests in French, Spanish, Mandarin via multilingual embeddings.

---

## Takeaways

This project demonstrates that modern AI systems require more than just LLM API calls. Effective procurement automation demands:

- **Structured orchestration** via frameworks like DSPy to manage complexity
- **Domain knowledge encoding** through signatures, reward functions, and business rules
- **Hybrid retrieval** combining vector search with deterministic validation
- **Engineering discipline** including type safety, testing, and configuration management

The procurement domain provides an ideal testbed for these techniques—sufficiently complex to require multi-step reasoning, yet constrained enough to validate outputs against hard rules.

---

**Technical Stack Summary**

- **Framework**: DSPy 2.5+ (Refine, ChainOfThought, Predict modules)
- **Vector Database**: Milvus 2.6+ with Docker deployment
- **LLM Provider**: OpenAI (GPT-4o for reasoning, text-embedding-3-small for retrieval)
- **Language**: Python 3.13 with type hints
- **Testing**: pytest, Ruff, Black
- **CI/CD**: GitHub Actions with pre-commit hooks
- **Data**: Faker-generated synthetic procurement data (20 suppliers, 20 contracts, 20 audits)

**Contact**: jyang297@uottawa.ca | [LinkedIn](https://www.linkedin.com/in/jiaqi-yang-b3014424b/)
