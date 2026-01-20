# Bir MCP: Enterprise AI Gateway for Model Context Protocol

**[Source](https://gitlab.com/koshmandk/bir_mcp)**

---

## Overview

| | |
|---|---|
| **Client** | Kapital Bank (Azerbaijan's largest private bank) |
| **Role** | Lead Developer / Architect |
| **Duration** | Ongoing |
| **Tech Stack** | Python, FastAPI, FastMCP, OAuth2/OIDC, Vault, Consul, LangChain |

---

## Project Description

Bir MCP is an enterprise-grade API gateway that enables AI assistants (Claude, GPT, etc.) to securely access internal tools and data sources through the Model Context Protocol (MCP) standard. It acts as a unified bridge between AI models and enterprise systems, with fine-grained access control, secrets management, and a self-service portal for users.

---

## The Challenge

Kapital Bank's IT operations teams needed AI assistants that could:

- **Access internal tools** — Jira, Confluence, GitLab, Grafana, SonarQube, Dataiku, SQL databases
- **Maintain security** — OAuth/SSO authentication, per-user permissions, secret management
- **Comply with enterprise requirements** — Audit logging, PII anonymization, rate limiting
- **Work with any MCP client** — Claude Desktop, Cursor, Windsurf, or custom agents

No existing solution provided this level of enterprise integration with the MCP standard.

---

## Solution Architecture

The system consists of several key layers:

- **MCP Clients**: Claude Desktop, Cursor, Windsurf, Custom Agents
- **MCP Protocol**: JSON-RPC over HTTP/SSE
- **Bir MCP Gateway**: Central authentication and middleware layer
- **Backend Services**: Vault (Secrets), Consul (Config), Logfire/LangSmith (Observability)

The gateway includes:
- OAuth/OIDC Authentication Layer (OIDCProxy, JWT Binding Validation, Token Exchange)
- Middleware Pipeline (Rate Limiting, Timeout, Permissions, Secrets Injection, Anonymization, Moderation, Logging)
- Mounted MCP Subservers (jira, confluence, gitlab, grafana, sonarqube, dataiku, sql, meta, debug, charts)

---

## Technical Implementation

### 1. MCP Server Gateway (Core)

Built on **FastMCP** framework with custom extensions:

- **Multi-tenant architecture** — Per-user configuration stored in Vault/Consul
- **Composable middleware** — Pluggable pipeline for security, observability, processing
- **Dynamic tool filtering** — Tools shown based on user permissions and available secrets
- **Proxy support** — Can mount external MCP servers via HTTP

### 2. OAuth/OIDC Integration

Full enterprise SSO integration:

- **OIDC Proxy** — Bridges enterprise IdP to MCP clients without DCR support
- **JWT Binding Validation** — Prevents token theft via IP/User-Agent fingerprinting
- **Token Exchange API** — Allows programmatic access token conversion
- **Session Management** — Encrypted cookies with configurable persistence

### 3. Permission System

Four-level permission model per MCP server:

| Level | Description | Tool Types |
|---|---|---|
| `disabled` | No access | None |
| `read` | Read-only operations | Query, list, search |
| `write` | Safe modifications | Create, update |
| `destroy` | Destructive operations | Delete, force actions |

### 4. Secrets Management

Per-user secrets stored securely:

- **Vault integration** — KV v1/v2 with async support
- **Consul fallback** — YAML-based config storage
- **Runtime injection** — Secrets injected into tool calls transparently
- **Validation** — Secrets tested against actual services before saving

### 5. Enterprise Tool Integrations

**10+ MCP subservers** with 50+ tools:

| Server | Tools | Capabilities |
|---|---|---|
| **GitLab** | 12 | Project info, file content, MR overview, search, create MR/branch |
| **Jira** | 8 | Issue details, search, comments, transitions, worklogs |
| **Confluence** | 6 | Page content, search, space info, page tree |
| **Grafana** | 5 | Dashboards, panels, alerts, annotations |
| **SonarQube** | 4 | Project metrics, issues, quality gates |
| **Dataiku** | 4 | Datasets, recipes, scenarios |
| **SQL** | 3 | Schema info, query execution (with table restrictions) |
| **Charts** | 2 | Vega-Lite chart generation |

### 6. User Portal (Gradio UI)

Self-service web interface with:

- **Chat Tab** — LangChain agent with streaming, tool calling, resource fetching
- **MCP Configs Tab** — Per-server permission selection, SQL table restrictions
- **Secrets Tab** — Token entry with validation status indicators
- **Docs Tab** — Embedded documentation

### 7. AI Agent (LangChain)

Built-in chatbot for testing and onboarding:

- **Tool loading** via `langchain-mcp-adapters`
- **Resource reading** — Custom tool to fetch MCP resources
- **LangSmith tracing** — Full observability of agent execution
- **Streaming responses** — Token-by-token output with message chunking

### 8. Security Features

- **Rate limiting** — Per-client with burst capacity
- **PII Anonymization** — Presidio (local) or Dataiku (API)
- **Content moderation** — Optional AI-based output filtering
- **Tool call logging** — Audit trail to Dataiku
- **Output truncation** — Configurable max length (100K chars default)

### 9. Observability

Multiple backends supported:

- **Logging** — Standard Python logging with filters
- **Logfire** — Structured logging with system metrics, MCP/OpenAI instrumentation
- **OpenTelemetry** — OTLP/gRPC export for custom backends
- **LangSmith** — Agent tracing with thread correlation

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Framework** | FastAPI, FastMCP, Starlette, Pydantic |
| **Auth** | Authlib (OAuth2), OIDC, JWT |
| **AI/LLM** | LangChain, LangGraph, LangSmith, OpenAI |
| **Databases** | Oracle (oracledb), PostgreSQL (psycopg), MySQL |
| **Secret Management** | HashiCorp Vault (hvac), Consul |
| **Enterprise APIs** | python-gitlab, atlassian-python-api |
| **UI** | Gradio |
| **Observability** | Logfire, OpenTelemetry, LangSmith |
| **Anonymization** | Presidio, Dataiku |
| **Infrastructure** | Docker, Gunicorn, uvicorn |

---

## Code Stats

| Metric | Value |
|---|---|
| Python source files | 70+ |
| Lines of code | ~9,200 |
| Test files | 30 |
| MCP subservers | 10 |
| MCP tools | 50+ |
| Dependencies | 35+ |

---

## Business Impact

### Developer Productivity
- **Self-service access** — Users configure their own tokens and permissions
- **Unified interface** — One gateway for all internal tools
- **AI-assisted workflows** — Natural language queries across systems

### Security & Compliance
- **Audit trail** — All tool calls logged with inputs/outputs
- **Fine-grained access** — Per-user, per-tool permissions
- **Data protection** — PII anonymization in outputs

### Scalability
- **Extensible architecture** — New MCP servers added via composition
- **HTTP proxy support** — External MCP servers integrated seamlessly
- **Multi-environment** — Debug/local/dev/preprod/prod stages

---

## Skills Demonstrated

### Backend Engineering
- Async Python with FastAPI/Starlette
- Middleware pipeline architecture
- OAuth2/OIDC integration
- Dependency injection (python-dependency-injector)

### Security
- Token binding and validation
- Secrets management with Vault/Consul
- Rate limiting and access control
- PII anonymization

### AI/ML Engineering
- LangChain agent development
- MCP protocol implementation
- Tool orchestration and resource management
- Observability with LangSmith

### Enterprise Integration
- REST API clients for GitLab, Jira, Confluence, Grafana
- Database connectivity (Oracle, PostgreSQL, MySQL)
- SSO/IdP integration

### DevOps
- Docker multi-stage builds
- Gunicorn/uvicorn deployment
- Environment-based configuration
- OpenTelemetry instrumentation

---

## Key Technical Decisions

1. **FastMCP over raw MCP SDK** — Better DX, middleware support, type safety
2. **OIDC Proxy pattern** — Enables OAuth with clients lacking DCR support
3. **Vault for user configs** — Proper secret management vs. database storage
4. **Middleware composition** — Clean separation of cross-cutting concerns
5. **Gradio for UI** — Rapid development, Python-native, good enough for internal tools
6. **Per-server permissions** — Balances security with usability

---

## Repository Structure

```
bir_mcp/
├── src/bir_mcp/
│   ├── app.py              # FastAPI app factory
│   ├── gateway.py          # MCP gateway construction
│   ├── middleware.py       # Security & processing middleware
│   ├── auth/               # OAuth, MCP auth, UI auth
│   ├── config/             # Server, user, SQL configuration
│   ├── core/               # Base classes, secrets, user info
│   ├── servers/            # MCP subserver implementations
│   │   ├── atlassian/      # Jira, Confluence
│   │   ├── git_lab/        # GitLab tools
│   │   ├── grafana/        # Grafana tools
│   │   ├── sql/            # Database tools
│   │   └── ...
│   ├── ui/                 # Gradio user portal
│   ├── anon/               # Anonymization (Presidio, Dataiku)
│   └── utils/              # Utilities
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # API integration tests
│   └── mcp_client/         # MCP protocol tests
├── Dockerfile
├── compose.yaml
└── pyproject.toml
```
