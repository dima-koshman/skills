# Directory Update Log

## 2026-08-16

* **Initialization**: Created the development concept bundle — a vendor-neutral knowledge graph for general software-development and distributed-systems concepts, split out from `okf-ai-engineering` so the AI-specific material stays focused. Structured as `communication/` (service contracts and transport) and `infrastructure/` (the layer around services), with a root [Development](/development.md) map concept.
* **Creation**: Added [Protocol Buffers](/communication/protobuf.md) — schema-first binary serialization, with field numbers as the evolution contract and the non-self-describing trade-off against JSON that makes schema distribution mandatory.
* **Creation**: Added [gRPC](/communication/grpc.md) — protobuf-as-IDL RPC with generated stubs, the four streaming shapes, and the operational primitives (deadlines, cancellation, channels, metadata, status codes) it standardizes; records the edge-facing trade-offs against REST and why HTTP/2 multiplexing pushes load balancing into the mesh data plane.
* **Creation**: Added [Service Mesh](/infrastructure/service-mesh.md) — the case for relocating cross-cutting call concerns out of per-service libraries, Istio's sidecar and ambient data planes with `istiod` as control plane, and the cost that makes early adoption a common mistake.
* **Creation**: Added [Data, Control & Management Planes](/infrastructure/planes.md) — the three-plane decomposition and its SDN origin, worked through Istio and Kubernetes, with the load-bearing consequence recorded: a correct data plane fails *static* on its last known config when the control plane is down.
