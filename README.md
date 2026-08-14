# 🛡️ PulseGuard AI

### A Safety-First Healthcare AI Assistant with a Deterministic Safety Firewall

> **Use deterministic logic where safety and predictability matter.  
> Use LLMs where natural-language understanding and generation matter.**

PulseGuard AI is a locally hosted healthcare AI prototype designed around a **defense-in-depth safety architecture**.

Instead of sending every healthcare query directly to a Large Language Model, PulseGuard first processes the request through a multi-stage safety pipeline that evaluates privacy, intent, risk, high-impact context, medical coverage, information sufficiency, retrieval evidence, and confidence.

Only requests that satisfy the configured safety conditions are allowed to proceed to Llama 3 for response generation.

The core design principle is:

> **The LLM should not be solely responsible for deciding whether the LLM should be allowed to answer.**

PulseGuard therefore separates **deterministic safety decisions** from **probabilistic language understanding and generation**.

---

# 🎯 Problem Statement

Large Language Models are powerful at understanding natural language and generating responses, but healthcare introduces additional challenges:

- Medical queries can contain sensitive personal information.
- Users can describe the same medical condition using many different expressions.
- LLMs can hallucinate or generate unsupported information.
- A model's refusal behavior is not a deterministic safety guarantee.
- Some queries require additional patient information before a meaningful response can be generated.
- High-risk situations should not depend solely on an LLM's interpretation.
- Sending every query to an LLM unnecessarily increases inference cost and latency.

PulseGuard explores a different architecture:

```text
                    User Query
                         │
                         ▼
              ┌─────────────────────┐
              │  Deterministic      │
              │  Safety Firewall    │
              └──────────┬──────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       Privacy         Intent          Risk
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                    High Impact
                         │
                         ▼
                 Medical Coverage
                         │
                         ▼
                   Sufficiency
                         │
                         ▼
                       RAG
                         │
                         ▼
                    Confidence
                         │
                         ▼
                  Decision Engine
                    │          │
             Unsafe │          │ Safe
                    ▼          ▼
             Safety Path     Llama 3
                                 │
                         Retrieved Context
                                 │
                                 ▼
                         Generated Response
```

🧠 Core Architectural Philosophy

PulseGuard follows one central principle:

Use deterministic mechanisms where predictability, auditability, and explicit safety policies matter, and use the LLM where natural-language interpretation and generation provide value.

Deterministic responsibilities
PII detection
Intent classification
Risk classification
High-impact detection
Medical coverage detection
Decision routing
Crisis responses
Emergency responses
Refusal responses
LLM responsibilities
Natural-language sufficiency interpretation
Structured extraction of information
Natural-language response generation
Reasoning over retrieved medical context

This separation prevents the LLM from becoming the only component responsible for safety decisions.

🛡️ Defense-in-Depth Architecture

PulseGuard does not assume that any single component is perfect.

Instead, multiple layers contribute to the final decision:
```
                    User Query
                         │
                         ▼
                  Privacy Guard
                         │
                         ▼
                 Intent Classifier
                         │
                         ▼
                  Risk Classifier
                         │
                         ▼
                   High Impact
                         │
                         ▼
                Medical Coverage
                         │
                         ▼
                  Sufficiency Check
                         │
                         ▼
                       RAG
                         │
                         ▼
                 Confidence Layer
                         │
                         ▼
                  Decision Engine
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
        Safety / Fallback        Llama 3
                                       │
                                       ▼
                                  Final Answer
```
The system therefore does not depend exclusively on:

Regex
RAG
Llama 3
A single confidence score
A single classifier

Each component contributes a signal to the overall decision process.

🔥 Why Not Just Use an LLM?

A simple architecture could be:
```
User
  ↓
LLM
  ↓
Answer / Refusal
```
PulseGuard instead uses:
```
User
  ↓
Safety Firewall
  ↓
Decision Engine
  ├── Unsafe → Deterministic Safety Response
  │
  └── Safe → RAG + Llama 3
```
The motivation is straightforward:

If a safety decision can be expressed using an explicit, testable rule, it should not unnecessarily depend on probabilistic model behavior.

For known blocked paths, PulseGuard can return deterministic responses without invoking the LLM.

This also avoids unnecessary inference and token usage.

🧩 Complete Pipeline

Each query moves through the following stages.

1. Privacy & PII Guard

The Privacy Guard checks the query for configured forms of personally identifiable information.

Currently supported patterns include:

Email addresses
Phone numbers
Social Security Numbers / configured identification patterns

Detected PII is redacted before downstream processing.
```
User Query
    │
    ▼
Privacy Guard
    │
    ├── PII detected → Privacy-safe response
    │
    └── No PII → Continue
```
Why?

The goal is to minimize unnecessary exposure of sensitive information to downstream components and the LLM.

Limitation

The current implementation is rule-based and cannot guarantee detection of every possible PII format.

This is a known limitation and an area for future improvement.

2. Intent Classification

The Intent Classifier determines the broad purpose of the query.

Current intent categories include:

Self-harm
Drug overdose / misuse
Violence
Illegal misuse
Medication guidance
Greeting / closure
Medical advice

The current implementation uses rule-based / regex-based heuristics.

Example:
```
"I want to overdose on these pills"
            ↓
      SELF_HARM / OVERDOSE
```
The intent signal contributes to the final Decision Engine rather than directly depending on the LLM.

3. Risk Classification

The Risk Classifier identifies potentially risky medical situations.

Examples include patterns associated with:

Chest pain
Breathing difficulty
Heart attack
Heavy bleeding
Other configured emergency symptoms
Self-harm / overdose patterns
Moderate-risk medical conditions

The classifier also incorporates negation-aware matching.

For example:
```
"I have chest pain"
        ↓
Potential risk

"I don't have chest pain"
        ↓
Negation detected
        ↓
Avoid obvious false positive
```

The classifier produces a risk signal that is consumed by the Decision Engine.

Important limitation

Rule-based detection cannot cover every possible way a user can describe a medical emergency.

Therefore:

The risk classifier is a safety layer, not a guarantee of complete emergency detection.

4. High-Impact Detection

Certain contexts require additional caution.

The current implementation considers contexts such as:

Pregnancy
Very young patients
Elderly patients
Immunocompromised patients
Anticoagulant use
Diabetes
Other configured high-impact contexts

For example:
```
Patient age < 5
        ↓
High-impact signal
```
or:
```
Pregnancy-related query
        ↓
High-impact signal
```
This signal is combined with other pipeline signals rather than being treated as a complete medical assessment.

5. Medical Coverage Detection

The Medical Coverage module determines whether the query is actually related to the medical domain.

It can identify:

Medical symptoms
Body parts
Medical conditions
Medical terminology
Medication-related terms
Non-medical topics

Examples:
```
"I have a headache"
        ↓
Medical coverage

"How do I reverse a linked list?"
        ↓
Non-medical
```
This prevents unrelated queries from unnecessarily entering the medical reasoning pipeline.

6. Sufficiency Checking

A healthcare query may be medical but still lack enough information for a useful response.

PulseGuard therefore checks whether the query contains basic information such as:

Age
Symptoms
Duration

The LLM can be used to extract these fields into a strict structured format.

Example:

{
  "age": 24,
  "symptoms": ["sore throat"],
  "duration": "2 days"
}

The important distinction is:

Llama 3 interprets the natural language; it does not make the final safety decision.

A deterministic/heuristic fallback is also available for cases where the LLM-based sufficiency check cannot be used.

7. Retrieval-Augmented Generation

PulseGuard uses Retrieval-Augmented Generation to provide medical-specific context to Llama 3.

The retrieval pipeline is:
```
User Query
    │
    ▼
Embedding Model
    │
    ▼
Query Embedding
    │
    ▼
Cosine Similarity
    │
    ▼
Similarity Threshold
    │
    ▼
Top-K Documents
    │
    ▼
Relevant Medical Context
    │
    ▼
Llama 3
Embedding Model
```
The project uses:

nomic-embed-text

The embedding model converts text into numerical vectors representing semantic information.

The vector dimension is determined by the embedding model rather than being universally fixed.

🔎 Why Embeddings?

Keyword matching requires similar words.

For example:

"shortness of breath"

and:

"difficulty breathing"

may describe a similar concept while using different words.

Embeddings allow the system to compare the semantic representation of the query and documents rather than requiring exact word matches.

📐 Cosine Similarity

PulseGuard uses cosine similarity to compare the query embedding with stored document embeddings.

Intuitively:

Cosine similarity measures how similarly two vectors are oriented.

A higher similarity indicates that the embedding model considers the texts more semantically related.
```
Query Embedding
       │
       ├──── Document A → high similarity
       ├──── Document B → low similarity
       └──── Document C → medium similarity
```
The system then retrieves the most relevant documents subject to the configured similarity threshold.

🔢 Top-K Retrieval

Suppose the knowledge base contains:

1,000,000 documents

and only:

10,000 documents

are potentially relevant.

Sending all of them to the LLM would be inefficient.

Instead:
```
1,000,000 documents
        ↓
Similarity Search
        ↓
Top-K
        ↓
Small relevant context
        ↓
Llama 3
```
This reduces unnecessary context and token usage.

🎚️ Similarity Threshold

The prototype uses a configurable similarity threshold.

A value such as:

0.45

was explored experimentally during development.

It is not claimed to be a universal medical threshold.

The purpose of the threshold is to prevent low-similarity documents from being treated as reliable supporting evidence.

If no sufficiently relevant documents are retrieved:
```
No relevant evidence
        ↓
Lower confidence
        ↓
Decision Engine
        ↓
Safer handling
```
This follows an important principle:

When the system does not have enough evidence, it is better to avoid confidently generating unsupported medical information.

🗄️ Local Knowledge Store

The current prototype stores its medical knowledge and embeddings locally using SQLite.

Why SQLite?

Serverless
Lightweight
Simple local setup
No separate database server
Suitable for a small prototype

For a much larger deployment, the retrieval layer could be migrated to a dedicated vector database or vector index.

🤖 Llama 3

Llama 3 is used as the generative model.

The model is intentionally used for tasks where natural-language capabilities are valuable rather than being used as the primary deterministic safety layer.

Current responsibilities
Structured sufficiency interpretation
Natural-language response generation
Reasoning over retrieved context
Producing user-facing responses

The model is run locally through:

Ollama
🖥️ Why Ollama?

The project was designed to be locally hosted.

Ollama provides a convenient runtime for local LLM inference.

This gives the prototype:

Local inference
No mandatory cloud LLM API dependency
Simplified experimentation
Better control over the local data flow
Easy model switching during development

Architecture:
```
PulseGuard
     ↓
Ollama
     ↓
Llama 3
     ↓
Local inference
🧠 Why Llama 3?
```
For this prototype, Llama 3 provides sufficient natural-language capabilities without requiring a large reasoning-focused model.

The deterministic safety pipeline handles the critical routing decisions, while Llama 3 handles language understanding and generation.

This allows the system to keep the LLM's role focused.

📝 System Prompt

The final LLM generation receives:
```
System Instructions
+
Retrieved Medical Context
+
User Query
```
The system instructions establish the model's role and expected behavior.

The retrieved documents provide domain-specific context.

The user query provides the actual request.

This allows a general-purpose LLM to produce a more controlled healthcare-oriented response without modifying the model's underlying parameters.

🧠 RAG vs Fine-Tuning

PulseGuard currently uses RAG rather than fine-tuning.

Fine-tuning

Fine-tuning modifies the model's learned parameters using additional training data.

RAG

RAG leaves the model unchanged and provides relevant external context during inference.
```
Fine-tuning
    ↓
Modify model parameters
```
```
RAG
    ↓
Retrieve knowledge
    ↓
Provide context
    ↓
Generate response
```
For this prototype, RAG is more suitable because the primary requirement is to provide medical-specific knowledge to a general-purpose model rather than retrain the model itself.

🧠 Hallucination Mitigation

LLM hallucination occurs when a model generates information that is incorrect, unsupported, or presented with unjustified confidence.

PulseGuard does not claim to eliminate hallucination.

Instead, it attempts to reduce the probability of unsupported responses using multiple layers:
```
Medical Query
      ↓
Safety Firewall
      ↓
Sufficiency
      ↓
Medical Retrieval
      ↓
Relevant Context
      ↓
Confidence
      ↓
Decision Engine
      ↓
Llama 3
```
RAG provides supporting context, while confidence and decision logic determine whether the system should proceed.

If relevant evidence cannot be retrieved, the system can choose a safer path instead of pretending that supporting evidence exists.

❤️ Decision Engine

The Decision Engine is the heart of the safety architecture.

It receives signals from the preceding modules and determines the final action.

Conceptually:
```
Privacy
Intent
Risk
High Impact
Medical Coverage
Sufficiency
RAG Evidence
Confidence
       │
       ▼
Decision Engine
       │
       ├── Safety Response
       ├── Clarification
       ├── More Information
       ├── Caution
       ├── Escalation
       └── Safe Response
```
The engine uses explicit priority-ordered rules.

This makes the critical safety routing:

Deterministic
Auditable
Testable
Explainable

The LLM is not asked:

"Should I answer this safely?"

Instead, the deterministic pipeline decides whether the LLM should be reached at all.

🚨 Example Decision Priority

The system gives higher priority to critical safety paths.

Conceptually:
```
Self-Harm / Crisis
        ↓
Emergency / High Risk
        ↓
Insufficient Information
        ↓
Moderate / High-Impact
        ↓
Low Confidence
        ↓
Safe Response
```
The exact priority is implemented through the Decision Engine's rule ordering.

This prevents strong RAG retrieval from automatically overriding a high-risk safety signal.

For example:

Risk = HIGH
RAG Confidence = HIGH

does not mean:

SAFE_TO_RESPOND

The risk signal remains the dominant safety consideration.

🧭 Escalation Router

The Decision Engine determines the appropriate action.

The Escalation Router determines what should happen downstream for actions requiring escalation.

This separation keeps the responsibilities independent.
```
Decision Engine
      ↓
Action
      ↓
Escalation Router
      ↓
Immediate / Review / None
```
The current prototype represents escalation through configured routing behavior rather than integration with an actual clinical support service.

🏗️ Separation of Responsibilities

The backend is intentionally modular.
```
Flask
   ↓
process_query.py
   ↓
Individual Modules
Flask
```
Responsible primarily for:

Receiving HTTP requests
Validating request structure
Returning HTTP responses
process_query.py

Acts as the orchestrator.

It:

Calls the modules
Passes information between stages
Collects signals
Sends the combined information to the Decision Engine
Coordinates response generation
Individual modules

Each module owns one major responsibility.
```
privacy_guard.py
    → Privacy


intent_classifier.py
    → Intent


risk_classifier.py
    → Risk


high_impact.py
    → High-impact context


medical_coverage.py
    → Medical domain detection


sufficiency_checker.py
    → Information sufficiency


retrieval_layer.py
    → RAG


confidence_calibrator.py
    → Confidence


safety_rules.py
    → Decision Engine


escalation_router.py
    → Escalation


response_generator.py
    → Response generation
```
This follows the Single Responsibility Principle and keeps the orchestration layer from becoming one large backend file.

🔄 Sequential Execution

For the current prototype, the modules execute sequentially and collect their signals.

This was intentional.

The goal was to make the complete decision path observable and easy to inspect during development.
```
Query
 ↓
Module 1
 ↓
Module 2
 ↓
Module 3
 ↓
...
 ↓
Decision Engine
```
Production optimization
For a production system, high-confidence safety conditions could short-circuit the pipeline.

For example:
```
Known critical self-harm pattern
        ↓
Immediate safety route
        ↓
Skip unnecessary downstream processing
```
This would reduce latency and unnecessary computation.

⚠️ Failure Handling Philosophy

Safety-critical failures should not automatically become:

SAFE

The desired production principle is:

Fail closed rather than fail open.

For example:
```
Risk Classifier Failure
        ↓
Risk = UNKNOWN
        ↓
Conservative handling
```
rather than:
```
Risk Classifier Failure
        ↓
Risk = SAFE
        ↓
LLM
```
Similarly, if the Decision Engine fails, the system should not assume that the request is safe to send to the LLM.

The current prototype has explicit fallback behavior in selected modules, while comprehensive failure isolation and fail-closed handling across every module remain production improvements.

🔬 Evaluation

Safety systems should be evaluated using both safe and risky queries.

The evaluation dataset should include:

True Positives

Risky query correctly detected.

True Negatives

Safe query correctly allowed.

False Positives

Safe query incorrectly flagged.

False Negatives

Risky query incorrectly allowed.

For a healthcare safety firewall, false negatives are particularly important.

Recall
Recall = TP / (TP + FN)

Recall answers:

"Of all genuinely risky queries, how many did the firewall detect?"

Precision
Precision = TP / (TP + FP)

Precision answers:

"Of all queries flagged as risky, how many were actually risky?"

PulseGuard would generally prioritize high recall for safety-critical detection while still monitoring precision to avoid making the system unnecessarily restrictive.

🧪 Testing Strategy

The project includes tests for major components.

Example test categories:
```
Privacy Tests
Risk Tests
Intent Tests
Medical Coverage Tests
Sufficiency Tests
Decision Engine Tests
V2 Component Tests
Full Pipeline Tests
```
Example commands:
```
python test_safety_filters.py
python test_risk_checker.py
python test_sufficiency_checker.py
python test_decision_engine.py
python test_medical_coverage.py
python test_v2_components.py
python test_full_pipeline.py
```
A future production evaluation would additionally include:

Large labeled safety datasets
Precision / recall analysis
False-negative analysis
False-positive analysis
Retrieval Recall@K
MRR / NDCG
Response grounding evaluation
Adversarial query testing
Prompt injection testing
Load testing
Failure-injection testing

🧱 Technology Stack
| Layer             | Technology                     |
| ----------------- | ------------------------------ |
| Frontend          | React                          |
| Backend           | Python                         |
| API Framework     | Flask                          |
| LLM Runtime       | Ollama                         |
| Generative Model  | Llama 3                        |
| Embedding Model   | nomic-embed-text               |
| Database          | SQLite                         |
| Retrieval         | Embeddings + Cosine Similarity |
| Safety Logic      | Python + Regex / Rules         |
| API Communication | HTTP / JSON                    |

📁 Project Structure
```
healthcare_llm_project/
│
├── app.py
├── index.html
├── requirements.txt
│
├── modules/
│   ├── config.py
│   ├── privacy_guard.py
│   ├── intent_classifier.py
│   ├── risk_classifier.py
│   ├── high_impact.py
│   ├── medical_extractor.py
│   ├── medical_coverage.py
│   ├── retrieval_layer.py
│   ├── sufficiency_checker.py
│   ├── confidence_calibrator.py
│   ├── safety_rules.py
│   ├── escalation_router.py
│   ├── response_generator.py
│   └── text_utils.py
│
├── data/
│   └── clinical_knowledge.db
│
├── clinical_guidelines/
│
├── logs/
│
└── tests/
```
🚀 Quick Start
1. Install Ollama

Install Ollama from:

https://ollama.com

Then pull the required models:
```
ollama pull llama3
ollama pull nomic-embed-text
```
2. Clone the repository
```
git clone <repo-url>
cd unanswerabilty-aware-ai-for-medical-use-
```
3. Create a virtual environment

Windows
```
python -m venv .venv
.venv\Scripts\activate
```
macOS / Linux
```
python -m venv .venv
source .venv/bin/activate
```
4. Install dependencies
```
pip install -r requirements.txt
```
5. Start the backend
```
python app.py
```
6. Run the full pipeline
```
python test_full_pipeline.py
```
🌐 Frontend

PulseGuard includes a React-based chat interface connected to the Flask backend.

The frontend:

Accepts healthcare queries
Sends HTTP requests to Flask
Displays pipeline responses
Maintains the chat experience
Presents deterministic and LLM-generated responses through the same interface

Architecture:
```
React
  │
  │ HTTP POST
  ▼
Flask
  │
  ▼
process_query.py
  │
  ▼
Safety Pipeline
  │
  ▼
Response
  │
  ▼
React
```
🔐 Security & Privacy Considerations

The current prototype includes:

PII detection
PII redaction
Local LLM inference
Local knowledge storage
Deterministic safety routing

However, the prototype does not claim to provide complete production security.

Production deployment would require:

Authentication
Authorization
HTTPS
Secure secret management
Rate limiting
Access controls
Data retention policies
Encryption where appropriate
Production-grade audit logging
Security testing
📈 Prototype vs Production

PulseGuard is intentionally designed as a small locally hosted prototype.

Current Prototype
```
Flask
   +
SQLite
   +
Local Ollama
   +
Llama 3
   +
Sequential pipeline
```
This keeps the system:

Simple
Explainable
Easy to develop
Easy to debug
Lightweight
Production Direction

A production architecture could evolve toward:
```
                Users
                  │
                  ▼
             Load Balancer
                  │
                  ▼
           Async API Layer
                  │
                  ▼
             Job Queue
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Safety Workers        LLM Workers
        │                   │
        ▼                   ▼
 PostgreSQL          Model Instances
        │                   │
        └─────────┬─────────┘
                  ▼
             Observability
```
Potential upgrades:

FastAPI / async API architecture
PostgreSQL
Dedicated vector database / vector index
Background workers
Queue-based LLM processing
Horizontal model scaling
Load balancing
Authentication
Rate limiting
Monitoring
Health checks
Production-grade failure handling
⚖️ Design Trade-offs
Why Flask?

For the current prototype:

Lightweight
Simple HTTP communication
Easy to develop
Sufficient for low concurrency
No requirement for complex asynchronous processing

FastAPI or Django could also support the project, but their additional capabilities were not necessary for the initial prototype.

Why SQLite?

SQLite was chosen because:

It is serverless
It stores data in a local database file
It requires minimal infrastructure
The prototype knowledge base is small

At larger scale, PostgreSQL and a dedicated vector search solution would be more appropriate.

Why not a Vector Database?

The current knowledge base is small enough that direct similarity comparison is acceptable.

At larger scale:
```
Small Knowledge Base
       ↓
SQLite + direct similarity
```
could become:
```
Large Knowledge Base
       ↓
Vector DB / ANN Index
       ↓
Efficient nearest-neighbor search
```
Why not Fine-Tune Llama 3?

The prototype primarily needs domain knowledge, not a modification of the model's fundamental behavior.

RAG allows the knowledge base to be updated without retraining the model.

⚠️ Known Limitations

PulseGuard is a research / portfolio prototype and should not be treated as a clinical decision-support system or medical device.

Known limitations include:

Rule-based detection

Regex and rules cannot cover every possible natural-language expression of a medical emergency.

This can result in false negatives.

PII detection

The current Privacy Guard only detects configured PII patterns.

Unrecognized formats may bypass that particular layer.

RAG

The knowledge base is relatively small.

The current similarity threshold is experimental and requires systematic evaluation.

Hallucination

RAG can reduce unsupported generation but cannot guarantee that Llama 3 will always produce correct information.

Post-generation validation

The current prototype does not provide a comprehensive deterministic validator for every generated response.

Escalation

The current escalation layer represents routing behavior rather than a real connection to doctors, emergency services, or clinical hotlines.

Scalability

The current local architecture is designed for prototype-scale usage rather than thousands of concurrent users.

Security

Production authentication, authorization, HTTPS, rate limiting, and hardened infrastructure are future requirements.

🔮 Future Roadmap
Phase 1 — Prototype
 Safety firewall
 Privacy guard
 Intent classification
 Risk classification
 High-impact detection
 Medical coverage
 Sufficiency checking
 RAG
 Confidence calibration
 Decision Engine
 Escalation routing
 Local Llama 3
 React frontend
 Flask API
 Structured logging
Phase 2 — Evaluation
 Build labeled safety dataset
 Measure precision and recall
 Analyze false negatives
 Analyze false positives
 Evaluate RAG Recall@K
 Tune similarity threshold
 Adversarial testing
 Prompt injection testing
Phase 3 — Production Engineering
 PostgreSQL
 Vector database / ANN index
 Async API architecture
 Background job queue
 Horizontal LLM workers
 Load balancing
 Authentication
 Authorization
 Rate limiting
 HTTPS
 Production observability
 Health checks
 Robust failure isolation
Phase 4 — Advanced Safety
 Post-generation safety validator
 Better PII detection
 Expanded medical risk taxonomy
 Stronger retrieval evaluation
 Human review integration
 Formal safety evaluation
 Continuous monitoring
💡 Key Engineering Lessons

PulseGuard was built around several practical engineering principles.

1. Don't use an LLM for everything

If a requirement can be expressed deterministically and safety depends on predictable behavior, a deterministic mechanism may be more appropriate.

2. RAG is grounding, not a guarantee

Retrieval provides additional evidence but does not eliminate hallucination.

3. Confidence should influence routing

If the system cannot find supporting evidence, it should not behave as though it has strong evidence.

4. Failure handling matters

A safety-critical component should not silently fail into a SAFE state.

5. Prototype architecture and production architecture are different

A lightweight sequential Flask + SQLite system can be completely reasonable for a local prototype while requiring significant changes for large-scale deployment.

6. Recall matters in safety detection

Missing a genuinely risky query is generally more concerning than unnecessarily flagging a safe query, although excessive false positives must also be controlled.

🎓 What Makes PulseGuard Different?

PulseGuard is not primarily an attempt to build a "smarter chatbot."

It is an attempt to build a controlled orchestration layer around a general-purpose LLM.

The central architecture is:
```
        Deterministic Safety
                │
                ▼
       ┌─────────────────┐
       │  Safety Firewall│
       └────────┬────────┘
                │
                ▼
          Evidence / RAG
                │
                ▼
          Confidence
                │
                ▼
        Deterministic Policy
                │
                ▼
             Llama 3
                │
                ▼
        Natural-Language Output
```
The goal is not to claim that any individual layer is perfect.

The goal is to make the overall system:

More predictable
More auditable
More conservative
More explainable
Easier to test
Easier to improve


📌 Project Status

Status: Local Research / Portfolio Prototype

Architecture: Safety-first, rule-gated LLM orchestration

Backend: Flask + Python

Frontend: React

LLM Runtime: Ollama

Generation Model: Llama 3

Embedding Model: nomic-embed-text

Database: SQLite

Retrieval: Embeddings + Cosine Similarity
