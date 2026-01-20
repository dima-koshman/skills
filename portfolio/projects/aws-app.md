# Speech AI: Multi-Modal AI Platform

**[Source](https://gitlab.com/koshmandk/moow-ai)** | **[Live Demo](https://ytynxmbg2f.eu-central-1.awsapprunner.com)**

---

## Overview

| | |
|---|---|
| **Type** | Side Project |
| **Role** | Full-Stack Developer |
| **Tech Stack** | Python 3.12, LangChain/LangGraph, OpenAI TTS, DALL-E 3, Gradio, Flutter, AWS |

---

## Project Description

A multi-modal AI platform with two applications:

1. **Story** — Converts text into narrated audio/video with multiple AI-assigned speakers, custom voice tones, and generated visuals
2. **Chgk** — An AI game show host that asks trivia questions, provides progressive hints, and evaluates answers

---

## Key Features

### App 1: Story (Text-to-Audio/Video)

Transforms written content into professionally narrated media with intelligent speaker assignment and visual generation.

**Text Analysis**
- Parses input text, filtering stage directions (lines starting with `#`)
- Splits into sentences using context-aware regex that handles edge cases (decimals, abbreviations, ellipses)
- Indexes each sentence for precise speaker assignment

**AI Character Assignment**

An LLM analyzes the text and produces:
- **Characters**: Name, voice selection, description (personality, accent, speaking style)
- **Sentence Ranges**: Which character speaks which sentences
- **Voice Instructions**: Per-segment tone, pacing, emotion, emphasis
- **Image Prompts**: Scene descriptions for visual generation

The AI chooses from 13 OpenAI voices, each with documented characteristics:
- Gender, vocal range (tenor/baritone/soprano/etc.)
- Direction responsiveness (1-5 scale for how well they follow custom instructions)
- Example assignments shown in the prompt for guidance

**Audio Generation**

Each sentence range is synthesized using OpenAI's TTS API:
- Model: `gpt-4o-mini-tts` with custom voice instructions
- Instructions combine character description + segment-specific direction
- Parameters: accent, emotional range, intonation, speed, whispering
- Parallel generation using async task groups

**Visual Generation**

Images generated from AI-crafted prompts:
- DALL-E 3 (1792x1024) or GPT Image-1-mini (1536x1024)
- Horizontal or vertical orientation based on target platform
- Each sentence range linked to an image ID for scene changes

**Video Assembly**

MoviePy combines audio and images:
- Streaming mode: yields segments as they complete for progressive playback
- Non-streaming mode: concatenates into single video file
- Sora-2 video generation available (currently disabled — expensive)

### App 2: Chgk (Quiz Game Show Host)

An AI host for "Что? Где? Когда?" (What? Where? When?) — a popular Russian intellectual quiz format.

**Question System**
- HuggingFace dataset: `ai-forever/MERA` (chegeka subset)
- Live API: `db.chgk.info/random` for real-time questions
- Deterministic shuffling using session ID as seed — prevents duplicates
- Batches of 5 questions with topic labels

**Answer Evaluation**

The AI host exhibits realistic game show behavior:
- **Correct Answer**: Acknowledges with enthusiasm, shares an interesting fact via web search
- **Incorrect Answer**: Offers progressive hints (vague → specific)
- **Partial/Close Answer**: Asks for more specificity, guides toward complete answer
- **User Gives Up**: Reveals answer with context and historical background

**AI Implementation**
- LangGraph agent with tool calling
- Web search enabled for fact enrichment
- Configurable thinking budget for reasoning models
- Models: GPT-4.1, GPT-5-mini, Gemini-3-pro, Gemini-2.5-flash

---

## Technical Implementation

### Backend Architecture

**Core Pipeline**
- FastAPI with mounted Gradio interface
- Async throughout — all AI calls non-blocking
- Parallel generation with `asyncio.TaskGroup`
- Progress tracking with custom `RemainingProgress` class

**AI Orchestration**
- LangChain for model abstraction and structured output
- LangGraph for agent workflows (Chgk)
- Pydantic models for type-safe AI responses

**Configuration**
- AWS Parameter Store for secrets (API keys)
- AWS AppConfig for dynamic configuration
- Environment-based settings (local vs prod)
- 10-minute TTL cache for secrets

### Frontend Options

**Gradio (Primary)**
- Two-tab interface: Story and Chgk
- Real-time progress updates
- Pre-loaded examples
- Model selection (local dev only)

**Flutter Mobile/Web**
- Clean Architecture with Riverpod state management
- Dio HTTP client with retry logic
- just_audio for playback
- freezed for immutable models

**Experimental**
- Reflex (Python-based React alternative)
- Streamlit prototypes

### Observability

- Logfire: request/response logging, system metrics
- LangSmith: agent traces, tool calls

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12, Dart |
| **AI Models** | GPT-4/5, Gemini 2.5/3, OpenAI TTS, DALL-E 3, Sora-2 |
| **Orchestration** | LangChain 0.3, LangGraph 0.5 |
| **Web** | FastAPI, Gradio 5.35 |
| **Mobile** | Flutter, Riverpod |
| **Media** | MoviePy, FFmpeg |
| **Cloud** | AWS (Parameter Store, AppConfig, App Runner) |
| **Monitoring** | Logfire, LangSmith |

---

## Code Stats

| Metric | Value |
|---|---|
| Python LOC | ~2,100 |
| Dart/Flutter LOC | ~1,200 |
| Test files | 7 |
| Deployment | Docker-ready |

---

## Skills Demonstrated

- **AI/ML Engineering**: LangChain agent development, prompt engineering for voice synthesis
- **Backend Development**: Async Python, FastAPI, parallel processing pipelines
- **Mobile Development**: Flutter with Clean Architecture, Riverpod state management
- **Cloud Infrastructure**: AWS services integration (Parameter Store, AppConfig, App Runner)
- **Media Processing**: Audio/video generation and assembly with MoviePy
