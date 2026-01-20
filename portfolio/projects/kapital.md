# Kapital Bank AI Platform

**[Source](https://gitlab.com/koshmandk/kapital-bank-ai)**

---

## Overview

| | |
|---|---|
| **Client** | Kapital Bank, Azerbaijan |
| **Role** | Lead Developer |
| **Period** | 2024 - Present |
| **Tech Stack** | Python 3.12, LangChain/LangGraph, FastAPI, Gradio, PostgreSQL/pgvector, SQLModel, Alembic, OAuth2/OIDC |

---

## Project Description

An internal AI platform for Kapital Bank employees, providing intelligent automation tools for common workplace tasks. The flagship application is the **Jira Service Desk Assistant** — a RAG-powered agent that recommends the correct Jira request type for any employee problem, provides self-help guidance, and generates prefilled ticket links.

The platform serves thousands of employees across the bank, handling requests in Azerbaijani, English, and Russian with automatic language detection.

---

## Key Features

### Jira Service Desk Assistant

The core application that transforms how employees interact with IT support:

**Intelligent Request Routing**
- Analyzes employee problems in natural language
- Recommends the most appropriate Jira request type from 100+ available types
- Provides self-help steps when users can resolve issues themselves
- Generates ready-to-use links with prefilled form fields based on conversation context

**Contextual Personalization**
- Integrates with corporate IAM system to fetch user context (department, role, office)
- Maintains per-user preferences stored in the database
- Pre-populates Jira fields with relevant user data

**Multi-Language Support**
- Automatic language detection (Azerbaijani, English, Russian)
- Responds in the user's language
- Handles code-switching within conversations

### AI-Powered Knowledge Base

**Automated Guide Generation Pipeline**

A daily pipeline that builds a living knowledge base:

1. **Data Collection** — Queries resolved Jira tickets via JQL, extracting request types, comments, resolution notes, and field values

2. **Intelligent Summarization** — An AI model processes the collected data to generate structured guides for each request type:
   - **Use Case**: When this request type should be created
   - **Self-Help**: Steps users can take to resolve the issue independently
   - **Resolution Pipeline**: How support teams typically resolve these tickets
   - **Input Fields**: Descriptions of what information is needed and why

3. **PII Handling** — All ticket content is anonymized using Presidio with custom patterns for Azerbaijan-specific identifiers (passports, VOEN, etc.)

4. **Embedding Generation** — Summaries are embedded using OpenAI's text-embedding-3 model and stored in pgvector for semantic retrieval

**Manual Override System**
- Google Sheets integration for manual guide curation
- Bidirectional sync between sheets and database
- Manual entries take weighted precedence in retrieval

### RAG Implementation

**Vector Database**
- PostgreSQL with pgvector extension, set up and configured from scratch
- HNSW indexing for fast approximate nearest neighbor search
- Separate collections for AI-generated and manually-curated content

**Ensemble Retrieval**
- Combines AI and manual knowledge bases with configurable weights
- Reciprocal Rank Fusion for result merging
- Service desk filtering for scoped searches
- Returns top candidates with relevance scores

**Agent Architecture**
- Custom LangGraph state machine for first-message flow (RAG → Think → Recommend)
- Standard ReAct loop for follow-up questions
- Tool-calling for detailed guide fetching, URL building, preference updates

---

## Technical Implementation

### Database Layer

**SQLModel + Alembic**
- Type-safe ORM models with Pydantic validation
- Automatic schema migrations on deployment
- Models: JiraRequest, InputRequestField, AiJiraRequestGuide, ManualJiraRequestGuide, User

**Schema Design**
- Composite primary keys for request type identification
- JSON columns for dynamic field configurations
- Cascade delete for data integrity
- Timestamps for incremental updates

### Authentication & Authorization

**OAuth2/OIDC Integration**
- Full OpenID Connect flow with corporate Keycloak
- Session-based authentication with encrypted cookies
- Automatic token refresh
- Seamless single sign-on experience

**User Context Extraction**
- UserInfo model populated from OIDC claims
- Fields: name, email, department, title, office, employee_id
- Used for request prefilling and personalization

### Web Application

**FastAPI + Gradio Hybrid**
- FastAPI for API endpoints, health checks, and MCP server
- Gradio for conversational UI with real-time streaming
- Separate authenticated and unauthenticated app mounts

**User Interface Features**
- Real-time display of tool calls and agent reasoning
- Like/dislike feedback buttons integrated with LangSmith
- Markdown rendering for links and formatted responses
- Mobile-responsive design

### Observability Stack

**Logfire**
- Full request/response tracing
- SQLAlchemy query logging
- HTTPX call instrumentation
- System metrics (CPU, memory, connections)

**LangSmith**
- Complete agent trace visualization
- Tool call inspection
- User feedback collection and aggregation
- Run comparison for debugging

**Google Sheets Export**
- Automated conversation export for manual review
- Quality scoring by QA team
- Feedback loop for prompt improvement

### MCP Server Integration

The toolkit is exposed as an MCP (Model Context Protocol) server, allowing:
- Claude Desktop integration
- API access for automated workflows
- Tool reuse across different AI applications

---

## Other Applications

The platform hosts additional AI tools:

- **Merge Request Review** — Automated GitLab MR analysis and suggestions
- **SQL Agent** — Natural language to SQL queries with result visualization
- **Governance Agent** — Policy compliance checking
- **Voice Assistant** — Speech-to-text input with TTS responses
- **Presentation Review** — Slide content analysis and feedback

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3.12 |
| **AI/LLM** | LangChain, LangGraph, OpenAI |
| **Web** | FastAPI, Gradio |
| **Database** | PostgreSQL, pgvector |
| **ORM** | SQLModel, Alembic |
| **Auth** | OAuth2/OIDC, Keycloak |
| **Observability** | Logfire, LangSmith |
| **Anonymization** | Presidio |
| **Infrastructure** | Docker |

---

## Results & Impact

- **Reduced ticket creation time** — Users find the right request type in seconds instead of browsing categories
- **Improved ticket quality** — Prefilled fields ensure complete information
- **Self-service enablement** — Many issues resolved without ticket creation
- **Knowledge preservation** — Institutional knowledge captured from resolved tickets

---

## Code Stats

| Metric | Value |
|---|---|
| Python LOC | ~10,600 |
| Type hints | Comprehensive throughout |
| Test suite | Pytest including E2E smoke tests |
| Deployment | Docker with non-root user |

---

## Skills Demonstrated

- **RAG Pipeline**: Complete implementation from data collection to embedding to retrieval
- **LangGraph Agents**: Custom state machines with multi-step reasoning
- **Vector Databases**: pgvector setup and optimization for production
- **OAuth Integration**: Corporate identity provider integration
- **PII Anonymization**: Custom patterns for Azerbaijan-specific identifiers
- **Knowledge Management**: Automated pipeline maintenance
- **Multi-Platform Observability**: Logfire, LangSmith, Google Sheets integration

---

## Engineering Decisions

- Chose pgvector over dedicated vector DBs for operational simplicity
- SQLModel for type-safe database access with Pydantic validation
- Ensemble retrieval to balance AI-generated and human-curated content
- Gradio for rapid UI iteration with streaming support
- Separate RAG database for isolation and scaling
