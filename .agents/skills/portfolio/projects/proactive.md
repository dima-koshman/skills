# Proactive: AI-Powered Telegram Bot with Autonomous Messaging

**[Source](https://gitlab.com/koshmandk/proactive)**

---

## Overview

| | |
|---|---|
| **Type** | Personal Project |
| **Role** | Solo Developer |
| **Status** | Active Development |
| **Tech Stack** | Python, LangChain, LangGraph, Telethon, PostgreSQL, Logfire |

---

## Project Description

Proactive is an AI-powered Telegram chatbot that operates in two distinct modes: responding to user messages in real-time (reactive) and autonomously sending targeted messages based on user preferences and conditions (proactive). The bot acts as a personal assistant that enriches conversations with real-world data, tracks user location, and makes autonomous decisions about when to contact users with relevant information like weather alerts.

---

## The Challenge

Building a personal AI assistant that goes beyond simple Q&A to:

- **Act autonomously** — Decide when and what to communicate without user prompting
- **Understand context** — Maintain conversation history and user preferences
- **Integrate real-world data** — Weather, location, timezone-aware messaging
- **Respect user preferences** — Customizable notification conditions and communication style

---

## Solution Architecture

The system consists of two bot modes running independently:

- **Reactive Bot**: Listens for incoming Telegram messages, invokes AI agent, responds
- **Proactive Bot**: Periodically evaluates each user, decides whether to send a message

Both modes share:
- PostgreSQL database for users, messages, preferences
- LangGraph ReAct agent with dynamic tool access
- External API integrations (weather, geocoding)

---

## Technical Implementation

### 1. Dual-Mode Bot Architecture

Abstract base class pattern with two implementations:

- **TelegramBot** — Base class with Telethon client, DB session management
- **ReactiveTelegramBot** — Event handler for incoming messages
- **ProactiveTelegramBot** — Scheduled loop checking if users need notifications

### 2. AI Agent (LangGraph)

ReAct agent with structured reasoning:

- **Dynamic tool access** — Weather tools enabled only if user location is known
- **Context-aware responses** — Full chat history passed to agent
- **Timezone awareness** — Messages formatted relative to user's local time
- **Customizable persona** — User preferences shape response tone and style

### 3. User Management

Comprehensive user data model:

- **Location tracking** — Latitude/longitude with reverse geocoding via Google Maps
- **Timezone detection** — Automatic timezone resolution from coordinates
- **Preferences persistence** — Proactive message conditions, communication style
- **Subscription system** — Different tiers with configurable message frequency

### 4. Weather Integration

Full OpenWeatherMap API integration:

| Feature | Description |
|---|---|
| Current weather | Temperature, conditions, humidity |
| Hourly forecast | 48-hour predictions |
| Daily forecast | 8-day outlook |
| Weather alerts | Severe weather notifications |
| Precipitation | Rain/snow probability |

### 5. Message Tracking

All conversations persisted:

- **Message categories** — human, AI, proactive_ai, system
- **Chat history retrieval** — Configurable history limits for agent context
- **Repetition avoidance** — Historical context prevents duplicate alerts

### 6. Observability

Multiple monitoring backends:

- **Logfire** — Structured logging with Celery, HTTPx, SQLAlchemy instrumentation
- **LangSmith** — LLM tracing with thread correlation
- **Tagged traces** — proactive/reactive labels for analysis

---

## Tech Stack

| Category | Technologies |
|---|---|
| **AI/LLM** | LangChain, LangGraph, OpenAI API, Google GenAI |
| **Messaging** | Telethon (Telegram client) |
| **Database** | PostgreSQL, SQLModel, SQLAlchemy, Alembic |
| **External APIs** | OpenWeatherMap, Google Maps (geocoding, timezone) |
| **Secrets** | Bitwarden Secrets Manager |
| **Observability** | Logfire, LangSmith |
| **Infrastructure** | Docker, Celery, Redis |
| **Data Processing** | Polars |

---

## Code Stats

| Metric | Value |
|---|---|
| Python source files | 15+ |
| Lines of code | ~1,500 |
| Test files | 5 |
| External integrations | 4 (Telegram, OpenWeatherMap, Google Maps, OpenAI) |

---

## Database Schema

| Table | Description |
|---|---|
| **Subscription** | Subscription types with model and proactive frequency |
| **AppUser** | User data, location, timestamps, preferences |
| **UserPreferences** | Name, location, timezone, notification conditions |
| **Message** | Conversation history with categories |

---

## Skills Demonstrated

### AI/ML Engineering
- LangGraph ReAct agent implementation
- Dynamic tool composition based on user state
- Context management and prompt engineering
- Multi-provider LLM support (OpenAI, Google)

### Backend Engineering
- Async Python with Telethon and HTTPX
- SQLModel/SQLAlchemy ORM patterns
- Database migrations with Alembic
- Abstract base class design patterns

### External Integrations
- Telegram Bot API via Telethon
- OpenWeatherMap API
- Google Maps Geocoding and Timezone APIs
- Bitwarden Secrets Manager

### DevOps
- Docker multi-service deployment
- Environment-based configuration (dev/prod)
- Observability instrumentation
- Secret management

---

## Key Technical Decisions

1. **LangGraph over raw LangChain** — Better control over agent reasoning loop
2. **Telethon over python-telegram-bot** — More flexibility, MTProto support
3. **SQLModel over raw SQLAlchemy** — Pydantic integration, cleaner models
4. **Bitwarden Secrets Manager** — Secure credential management without .env files
5. **Dual-bot architecture** — Clean separation of reactive and proactive concerns
6. **Logfire for observability** — Native Python support, good LangChain integration

---

## Repository Structure

```
Proactive/
├── src/
│   ├── proactive/
│   │   ├── ai.py              # Agent invocation, prompt building
│   │   ├── config.py          # Configuration, secrets, logging
│   │   ├── core.py            # Core functions (location, messages)
│   │   ├── tools.py           # AI toolkit (weather, preferences)
│   │   ├── utils.py           # Utilities (caching, timezone)
│   │   ├── bot/
│   │   │   ├── base.py        # TelegramBot base class
│   │   │   ├── reactive.py    # Reactive bot implementation
│   │   │   └── proactive.py   # Proactive bot implementation
│   │   ├── external/
│   │   │   ├── weather.py     # OpenWeatherMap integration
│   │   │   └── google.py      # Google Maps APIs
│   │   └── sql/
│   │       ├── models.py      # Database models
│   │       └── utils.py       # DB utilities
│   ├── launch_bot.py          # Entry point
│   ├── admin.py               # Admin tasks
│   └── tasks.py               # Celery tasks
├── test/
├── alembic/                   # Migrations
├── Dockerfile
├── compose.yaml
└── pyproject.toml
```
