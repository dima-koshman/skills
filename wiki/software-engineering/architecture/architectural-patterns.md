# Architectural Patterns

Choose component boundaries, communication styles, and dependency directions according to the forces acting on a system.

Primary reference: [Architectural Metapatterns: The Pattern Language of Software Architecture](https://metapatterns.io/), by Denys Poltorak and Lars Noodén.

Sources checked: 2026-10-10.

## Design framing

An architectural pattern describes a recurring arrangement of components and
their responsibilities. Architectural Metapatterns groups patterns with similar
structure and function into broader families, making it easier to compare
designs and understand their relationships. Its diagrams use abstraction level,
subdomain, and sharding as coordinates. Treat this taxonomy as a useful model;
a real system can combine several patterns. See the book's
[metapatterns introduction](https://metapatterns.io/introduction/metapatterns/).

Keep two decisions explicit: how to divide responsibilities, and where to run
them. A module boundary can exist within one process; turning it into a service
adds a network and deployment boundary. Fowler's
[Microservice Trade-Offs](https://martinfowler.com/articles/microservice-trade-offs.html)
explains the benefits of independent deployment alongside latency, partial
failure, consistency, and operational costs.

The central tension is between cohesion and decoupling. Keep tightly related
work together, while isolating parts that need to change independently. The
balance depends on domain knowledge, team ownership, consistency needs, and
runtime constraints. The book's
[Cohesers and decouplers](https://metapatterns.io/analytics/the-heart-of-software-architecture/cohesers-and-decouplers/)
is a useful vocabulary for discussing those forces.

## Patterns worth keeping in the working toolkit

The following is a practical synthesis, not a complete taxonomy or a ranking.

| Pattern | Useful when | Cost or question to make explicit |
| --- | --- | --- |
| Modular monolith | Domain modules need clear ownership while running in one deployment remains sufficient | Do module contracts hold, or do changes routinely cross their boundaries? |
| Layers | Application workflows, domain rules, and infrastructure have distinct responsibilities | Does each layer own a meaningful responsibility, or only forward calls? |
| Services | Components need independent releases, scaling, or operational isolation | Can the team handle remote failures, data ownership, and compatibility? |
| Ports and adapters | Core behavior should be testable independently of protocols, storage, or vendors | Do interfaces express application needs, or copy the current vendor's API? |
| Pipeline / pipes and filters | Processing consists of composable stages | Define stage contracts, ordering, and failure recovery |
| Proxy / gateway | Routing or shared policies belong at a common entry point | Account for availability, trust boundaries, and added request processing |
| Orchestrator | A workflow coordinates several components | Define workflow state, recovery, and responsibility for partial completion |
| Plugins | A stable core needs replaceable extensions | Define extension contracts, compatibility, and supported combinations |

Use [system topologies](https://metapatterns.io/introduction/system-topologies/)
for the structural overview. For deeper definitions, consult Cockburn's original
[Ports and Adapters article](https://alistair.cockburn.us/hexagonal-architecture),
Hohpe and Woolf's
[Pipes and Filters](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PipesAndFilters.html),
and the book's
[Proxy](https://metapatterns.io/extension-metapatterns/proxy/),
[Orchestrator](https://metapatterns.io/extension-metapatterns/orchestrator/), and
[Plugins](https://metapatterns.io/implementation-metapatterns/plugins/) chapters.

## Communication and data ownership

The book compares three ways to connect components:

- **Orchestration:** a workflow owner directs the steps. Useful when a use case
  spans components and its sequence needs to remain visible and easy to change.
- **Choreography:** components react to events. Useful for loosely coupled
  reactions; the end-to-end workflow can become harder to reconstruct.
- **Shared data:** components integrate through a common data model. Convenient
  access comes with coupling to schemas and their evolution.

These styles can coexist. Review where coupling actually lives: in workflow
code, event contracts, or shared schemas. See
[Comparison of communication styles](https://metapatterns.io/foundations-of-software-architecture/arranging-communication/comparison-of-communication-styles/).

For a concrete design, record who owns each write, which operations must be
atomic, what stale reads are acceptable, and how retries avoid duplicate side
effects. These are decision questions to resolve before selecting infrastructure.

## Applying the patterns to enterprise AI systems

These examples are design lenses, not an audit of any implementation:

- An [MCP gateway](../../ai-engineering/enterprise/mcp-gateway.md) can combine
  proxy routing, a policy pipeline, and adapters to downstream systems.
- An [agent](../../ai-engineering/agents/agent.md) can coordinate a use case as an
  orchestrator. Tool interfaces and workflow state deserve separate attention.
- A [RAG](../../ai-engineering/context/rag.md) ingestion flow can be modeled as
  stages for extraction, normalization, chunking, and indexing.
- A [service mesh](../infrastructure/service-mesh.md) moves communication policy
  into infrastructure. Evaluate its operational cost against the duplication it
  removes from services.

When reviewing a design, ask what changes together, which boundary protects
independent change, and which failure must be contained. Draw the request path
and state owners, then compare a simpler arrangement against the proposed one.
The existing [simplicity note](../reliability/simplicity.md) complements this:
reduce accidental complexity and keep APIs purposeful.

## Selected reading

Start with the first three; use the remaining chapters when a matching design
question arises. The selection favors architecture decisions over memorizing
pattern names.

| Chapter | Why read it |
| --- | --- |
| [System topologies](https://metapatterns.io/introduction/system-topologies/) | A map of architectural families and combinations beyond the usual monolith-versus-microservices discussion |
| [Cohesers and decouplers](https://metapatterns.io/analytics/the-heart-of-software-architecture/cohesers-and-decouplers/) | Explain which forces pull components together or apart |
| [Comparison of communication styles](https://metapatterns.io/foundations-of-software-architecture/arranging-communication/comparison-of-communication-styles/) | Compare workflow ownership, event reactions, and schema coupling |
| [Hexagonal Architecture](https://metapatterns.io/implementation-metapatterns/hexagonal-architecture/) | Explore adapter placement, dependency isolation, and leaky abstractions |
| [Proxy](https://metapatterns.io/extension-metapatterns/proxy/) | Separate routing, protocol translation, and common policy from downstream logic |
| [Orchestrator](https://metapatterns.io/extension-metapatterns/orchestrator/) | Understand the component that owns cross-component use cases |
| [Plugins](https://metapatterns.io/implementation-metapatterns/plugins/) | Think through extensibility and the stability of extension interfaces |
| [Architecture and product life cycle](https://metapatterns.io/analytics/architecture-and-product-life-cycle/) | Consider how boundaries may change as domain knowledge and maintenance needs evolve |

Read the book's classifications and lifecycle story as the authors' model.
Categorical performance statements are prompts for measurement; component
placement and actual call paths matter. Use the original sources below to
check a pattern's intent before treating a taxonomy as a design prescription.

## Complementary primary sources

- [Alistair Cockburn: Hexagonal architecture, original 2005 article](https://alistair.cockburn.us/hexagonal-architecture) — the inside/outside boundary and running application behavior independently of its UI and database.
- [Martin Fowler: Microservice Trade-Offs](https://martinfowler.com/articles/microservice-trade-offs.html) — modularity and independent deployment weighed against distribution and operational complexity.
- [Gregor Hohpe and Bobby Woolf: Pipes and Filters](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PipesAndFilters.html) — composable processing steps connected through common message interfaces.
- [Google SRE book: Simplicity](https://sre.google/sre-book/simplicity/) — reliability through reducing accidental complexity, keeping APIs small, and making changes understandable.
