---
type: Concept
title: Metastable Failures
description: Outages that persist after their trigger is gone, because the degraded system does extra work (retries,
  cache misses) that keeps it overloaded — fixed by attacking the feedback loop, not the trigger.
tags:
- software-engineering
- reliability
- distributed-systems
parent: /software-engineering/reliability.md
related:
- /software-engineering/reliability/sre.md
- /ai-engineering/enterprise/llm-gateway.md
- /software-engineering/infrastructure/service-mesh.md
- /software-engineering/distributed-systems/openai-habitat.md
sources:
- id: bronson-hotos21
  resource: https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf
  title: Metastable Failures in Distributed Systems (HotOS '21)
  author: Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, Timothy Zhu
  last_modified: '2021-06-03T00:00:00Z'
- id: huang-osdi22
  resource: https://www.usenix.org/conference/osdi22/presentation/huang-lexiang
  title: Metastable Failures in the Wild (OSDI '22)
  author: Lexiang Huang, Matthew Magnusson, Abishek Bangalore Muralikrishna et al.
  last_modified: '2022-07-11T00:00:00Z'
- id: brooker-metastability
  resource: https://brooker.co.za/blog/2021/05/24/metastable/
  title: Metastability and Distributed Systems
  author: Marc Brooker
  last_modified: '2021-05-24T00:00:00Z'
- id: brooker-retries
  resource: https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
  title: Timeouts, retries, and backoff with jitter (AWS Builders' Library)
  author: Marc Brooker
  last_modified: '2019-12-05T00:00:00Z'
- id: aws-load-shedding
  resource: https://builder.aws.com/content/3Eun1EEyX6p2e3VYNyRLSJzLuMV/using-load-shedding-to-avoid-overload
  title: Using load shedding to avoid overload (AWS Builders' Library)
  author: AWS (David, Sr. Principal Engineer)
  last_modified: '2019-12-05T00:00:00Z'
- id: fail-at-scale
  resource: https://blog.acolyer.org/2015/11/19/fail-at-scale-controlling-queue-delay/
  title: Fail at Scale and controlling queue delay (secondhand summary of Ben Maurer, ACM Queue 2015)
  author: Adrian Colyer
  last_modified: '2015-11-19T00:00:00Z'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-10-16T16:00:00+04:00'
---

A metastable failure is an outage that **outlives its cause**. A trigger knocks the system into a bad
state, and the system stays there after the trigger is gone, because being in the bad state makes it do
extra work that keeps it overloaded.[^bronson-hotos21]

## Why "metastable"

The word comes from physics: a ball resting in a small dip on a hillside. Small nudges don't move it, but
one big push sends it down the hill, and it can't roll back up on its own. A system is in the same
position when it handles its load only *because* it is efficient — warm caches, few retries. That
efficiency is what a trigger destroys.

## The three states

Bronson et al. describe a lifecycle:[^bronson-hotos21]

1. **Stable.** Load is low enough that the system recovers from any trigger by itself.
2. **Vulnerable.** Load rises above a threshold that is "implicit and invisible". The system is healthy
   and not overloaded, and can run like this for months. Many production systems run here all the time,
   because it is far more efficient.
3. **Metastable failure.** A trigger (spike, slow dependency, cache loss, deploy) starts a **sustaining
   effect**, a feedback loop that keeps goodput (useful work completed) near zero. Leaving requires a
   strong push: rebooting, or cutting load far below what the system normally handles.

The outage is usually blamed on the trigger, but the root cause is the sustaining effect. Failures that
end when the trigger ends, like a denial-of-service attack, are not metastable.[^bronson-hotos21]

## Two classic loops

- **Retry storm.** The database slows; clients time out and retry; retries add load; the database slows
  further. Three retries at each of five layers can multiply load on the bottom layer
  243×.[^brooker-retries]
- **Lost cache.** With a 90% hit rate, the app handles 3,000 QPS against a database that handles 300.
  Above 300 QPS it is vulnerable. If the cache is lost, the database overloads, its queries time out, and
  the cache never refills, because the app only fills it from successful queries: a 10× query
  amplification that sustains itself.[^bronson-hotos21]

In a study of 22 metastable failures at 11 organizations, at least 4 of the 15 major AWS outages of the
past decade were of this kind.[^huang-osdi22]

A less obvious loop: **LIFO connection reuse.** OpenAI's Python storage service used aiohttp, which reuses
the most recently returned connection. Connections to slow server processes return last, so they are
picked first, and the slow processes get even more work. Overloaded processes stayed overloaded after the
bursty client stopped, until restarted. FIFO reuse broke the loop. See
[OpenAI Habitat](/software-engineering/distributed-systems/openai-habitat.md).

## Making a system resilient

The goal is to break the loop: when the system is degraded, it must do *less* work per request, not more.

| Technique | What it does |
| --- | --- |
| **Limit retries** | Retry at one layer only, with exponential backoff and jitter.[^brooker-retries] A retry budget (a cap on retries as a share of requests) stops retries when everything is failing. |
| **Shed load early and cheaply** | Reject excess requests at the door, so accepted ones finish before clients time out. Track goodput, not throughput.[^aws-load-shedding] |
| **Don't do doomed work** | Propagate deadlines; drop requests whose client already gave up; cap queue wait time instead of letting queues grow.[^aws-load-shedding] |
| **Control queues** | CoDel: when a queue stays non-empty too long, give new requests a short timeout. Adaptive LIFO: under overload, serve the newest requests first, since they can still meet deadlines.[^fail-at-scale] |
| **Prioritize** | Give retries lower priority than first attempts; finish started work before new work.[^bronson-hotos21][^aws-load-shedding] |
| **Recover-friendly design** | A read-through cache keeps filling from slow queries even after the client gave up, so the hit rate climbs back; a look-aside cache cannot.[^bronson-hotos21] |
| **Circuit breakers** | Stop calling a failing dependency entirely for a while.[^bronson-hotos21] |
| **Know the threshold** | Load-test past the breaking point, with the trigger included (e.g. a cold cache). Small-scale tests may miss loops that only appear at full scale.[^bronson-hotos21][^aws-load-shedding] |
| **Value cold-path capacity** | Optimizations that only help the common case (a better cache hit rate, then shrinking the database) push the system deeper into the vulnerable state.[^bronson-hotos21] |

Brooker's framing: target the feedback loop that sustains the failure, not the trigger; control theory
offers tools for that.[^brooker-metastability]

## In an LLM gateway

SDK retries in each client, gateway retries, provider 429s, and a slow guardrail or NER step in the
request path can form a retry storm. Check that only one layer retries, and that the gateway sheds load
before its queues fill. See [LLM Gateway](/ai-engineering/enterprise/llm-gateway.md).

A [service mesh](/software-engineering/infrastructure/service-mesh.md) can own timeouts, retries and circuit
breaking for all services in one place, but deadline handling, prioritization and degradation stay in the
application.

[^bronson-hotos21]: Bronson, Aghayev, Charapko, Zhu, HotOS 2021.
[^huang-osdi22]: Huang et al., OSDI 2022.
[^brooker-metastability]: Marc Brooker, 2021-05-24.
[^brooker-retries]: Marc Brooker, AWS Builders' Library.
[^aws-load-shedding]: AWS Builders' Library.
[^fail-at-scale]: Adrian Colyer's summary of Ben Maurer's ACM Queue article (secondhand).
