---
type: Concept
title: LLM Browser Use
description: How LLMs operate real web browsers — the browser driver, the page representation the model reads, the control style and the hosting, with Playwright, Stagehand and Browserbase as examples.
tags:
- ai-engineering
- agents
- browser-automation
parent: /ai-engineering/harness.md
related:
- /ai-engineering.md
- /ai-engineering/harness/mcp.md
- /ai-engineering/context/tool-result-offloading.md
- /ai-engineering/harness/tools.md
- /ai-engineering/harness/sandboxes.md
- /ai-engineering/security.md
sources:
- id: playwright-intro
  resource: https://playwright.dev/docs/intro
  title: Playwright installation and overview
  author: Microsoft
- id: playwright-locators
  resource: https://playwright.dev/docs/locators
  title: Playwright locators
  author: Microsoft
- id: playwright-aria
  resource: https://playwright.dev/docs/aria-snapshots
  title: Playwright ARIA snapshots
  author: Microsoft
- id: playwright-repo
  resource: https://github.com/microsoft/playwright
  title: microsoft/playwright
  author: Microsoft
- id: playwright-mcp
  resource: https://github.com/microsoft/playwright-mcp
  title: microsoft/playwright-mcp
  author: Microsoft
- id: stagehand-quickstart
  resource: https://docs.stagehand.dev/v4/first-steps/quickstart
  title: Stagehand quickstart
  author: Browserbase
- id: stagehand-act
  resource: https://docs.stagehand.dev/v4/basics/act.md
  title: Stagehand act
  author: Browserbase
- id: stagehand-extract
  resource: https://docs.stagehand.dev/v4/basics/extract.md
  title: Stagehand extract
  author: Browserbase
- id: stagehand-models
  resource: https://docs.stagehand.dev/v4/configuration/models
  title: Stagehand models configuration
  author: Browserbase
- id: stagehand-browser
  resource: https://docs.stagehand.dev/v4/configuration/browser
  title: Stagehand browser configuration
  author: Browserbase
- id: stagehand-caching
  resource: https://docs.stagehand.dev/v4/best-practices/caching.md
  title: Stagehand caching
  author: Browserbase
- id: stagehand-repo
  resource: https://github.com/browserbase/stagehand
  title: browserbase/stagehand
  author: Browserbase
- id: browserbase-overview
  resource: https://docs.browserbase.com/introduction/what-is-browserbase
  title: What is Browserbase?
  author: Browserbase
- id: browserbase-sessions
  resource: https://docs.browserbase.com/platform/browser/getting-started/create-browser-session.md
  title: Create a browser session
  author: Browserbase
- id: browserbase-playwright
  resource: https://docs.browserbase.com/welcome/quickstarts/playwright.md
  title: Browserbase Playwright quickstart
  author: Browserbase
- id: browserbase-contexts
  resource: https://docs.browserbase.com/platform/browser/core-features/contexts.md
  title: Browserbase contexts
  author: Browserbase
- id: browserbase-captcha
  resource: https://docs.browserbase.com/platform/identity/captcha-solving.md
  title: Browserbase CAPTCHA solving
  author: Browserbase
- id: browserbase-proxies
  resource: https://docs.browserbase.com/platform/identity/proxies.md
  title: Browserbase proxies
  author: Browserbase
- id: browserbase-pricing
  resource: https://www.browserbase.com/pricing
  title: Browserbase pricing
  author: Browserbase
- id: claude-computer-use
  resource: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
  title: Claude computer use tool
  author: Anthropic
- id: chase-late-2026
  resource: https://www.langchain.com/blog/context-engineering-challenges-late-2026
  title: New context engineering challenges in late 2026
  author: Harrison Chase
  last_modified: '2026-11-02'
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-04T12:00:00+04:00'
stale_after: '2027-02-04T00:00:00+04:00'
---

An LLM cannot touch a browser on its own. Something has to drive the browser, turn the page into input the model can read, decide who chooses the next step, and host the browser. These are separate choices, and the tools below each cover different ones.

| Layer | Question | Examples |
| --- | --- | --- |
| Driver | What clicks and types in the browser? | Playwright, Stagehand |
| Page representation | What does the model read? | Accessibility tree, screenshots |
| Control style | Who decides the next step? | Your code or the model |
| Hosting | Where does the browser run? | Your machine, Browserbase |

# Page representation

An **accessibility tree** is structured text: roles, names, attributes and values. Playwright serializes it as YAML, with nodes such as `- button "Toggle" [pressed=true]`.[^playwright-aria] It needs no vision model. Its size is still a real cost: the Playwright MCP README warns about "verbose accessibility trees" filling model context.[^playwright-mcp] Playwright MCP and Stagehand both use this form.[^playwright-mcp][^stagehand-act]

A **screenshot** is pixels. Claude's computer use tool works this way: the model gets screenshots from your code, returns actions such as a click at a coordinate, and your application runs them.[^claude-computer-use] This reaches anything on a screen. Anthropic says the browser use tool is the closer fit for tasks that stay inside webpages.[^claude-computer-use]

Both forms are large objects, and Harrison Chase lists managing them as an open context problem for browser agents.[^chase-late-2026] [Tool result offloading](/ai-engineering/context/tool-result-offloading.md) is one option for snapshots. It doesn't solve images on its own.

# Control styles

| Style | Who picks the next step | LLM calls | Example |
| --- | --- | --- | --- |
| Scripted | Your code | None | Playwright |
| LLM per step | Your code, with the LLM resolving each step | Per instruction, unless replayed or cached | Stagehand |
| Agent loop, structured page | The model | Every turn | Playwright MCP |
| Agent loop, pixels | The model | Every turn | Claude computer use |

As a rule of thumb (my reading, not from the sources), move down the table only as far as the task needs. A known flow on stable pages should be a script. A known flow on pages that change suits LLM per step. An unknown goal needs an [agent](/ai-engineering.md#agent) loop, which costs the most and is the least repeatable.

# Playwright

Playwright is Microsoft's end-to-end test framework for Chromium, WebKit and Firefox, with Node.js, Python, Java and .NET bindings.[^playwright-intro] It is Apache-2.0 licensed.[^playwright-repo] The core library needs no LLM: you write the steps.

Locators are its central abstraction. `getByRole()` is the recommended first choice, an element is located afresh on every action, and a locator throws if more than one element matches.[^playwright-locators] Those rules are what make scripts resilient, and they are also what an LLM layer is trying to avoid writing by hand.

[Playwright MCP](https://github.com/microsoft/playwright-mcp) exposes browser actions as [MCP](/ai-engineering/harness/mcp.md) tools, so a model can drive the browser through accessibility snapshots. Its README recommends the CLI plus skills for coding agents, because that avoids loading large tool schemas and accessibility trees into context. It suggests MCP for long-running loops where continuous browser context outweighs token cost.[^playwright-mcp]

# Stagehand

Stagehand is Browserbase's MIT-licensed SDK for TypeScript, Python and Go.[^stagehand-repo] It keeps your code in charge of the steps and uses an LLM you configure to resolve each one against the current page. Notes below describe v4.

| Call | LLM used? | Returns |
| --- | --- | --- |
| `act("click the login button")` | Yes, to find the target | Performs one action |
| `act(action)` with an `Action` from `observe` | No, deterministic replay[^stagehand-act] | Performs that action |
| `extract("extract the price", Price)` | Yes | Data validated against the schema |
| `observe("find submit buttons")` | Yes | List of `Action` objects (selector, description, method, arguments) |

The model reads the page's accessibility tree, with every frame merged into one snapshot.[^stagehand-act] `extract` can also send a viewport screenshot on request.[^stagehand-extract]

Structured output comes from the model. Stagehand turns the Pydantic class (Zod in TypeScript) into a JSON schema, asks the model for that format, and validates the result before returning it.[^stagehand-extract] If the model returns plain text or content that does not match, the call fails rather than degrading silently.[^stagehand-models] Models therefore need structured-output support.

The useful pattern is to call `observe` once, keep the `Action`, and replay it. Replay skips inference, the page snapshot and the DOM-settle wait. `act` also has a `selfHeal` option that re-infers an action when its recorded selector breaks.[^stagehand-act]

The SDK and its bundled browser runtime run on your machine. The docs mention no separate server process: you `pip install stagehand`, and `local_browser.launch()` starts your installed Chrome.[^stagehand-quickstart][^stagehand-browser] It reads no environment variables, so keys are passed explicitly.[^stagehand-quickstart]

Built-in LLM providers are OpenAI, Anthropic, Google, Groq and Cerebras, using your own key. There is no base URL option, so self-hosted or offline models go through a callback passed as `model`, which must return content matching the schema.[^stagehand-models] The docs list "Local/offline" for this route but show no Ollama example, so using Ollama this way is an inference from the callback contract.

# Browserbase

Browserbase is a hosted platform for browsing agents. It offers cloud browsers, search, page fetch, functions, a model gateway and agent identity under one API key.[^browserbase-overview] A session is one isolated browser in the cloud, with a CDP connect URL, a live debug URL and a replay.[^browserbase-sessions] It is a hosting layer, so a plain Playwright script can use it:[^browserbase-playwright]

```python
session = bb.sessions.create()
browser = chromium.connect_over_cdp(session.connect_url)
page = browser.contexts[0].pages[0]
```

| Adds over a local browser | Detail |
| --- | --- |
| CAPTCHA solving | On by default, can take up to 30 seconds[^browserbase-captcha] |
| Proxies | Built-in with geolocation, or your own[^browserbase-proxies] |
| Persistent logins | Contexts keep cookies and storage across sessions; don't share one between simultaneous sessions[^browserbase-contexts] |
| Recording | Session replay and logging on by default[^browserbase-sessions] |
| Stagehand extras | Model Gateway and server-side cache, unavailable on local browsers[^stagehand-browser] |

The Stagehand cache is on by default for eligible calls. Its key uses the instruction, page content, call options and URL, and values you pass as variables reach the cache service, so turn it off for calls carrying credentials.[^stagehand-caching]

# Cost

| Part | Local browser | Browserbase |
| --- | --- | --- |
| Software | Playwright and Stagehand are free and open source[^playwright-repo][^stagehand-repo] | Same |
| Browser | Free | Free tier: 1 browser hour, 3 concurrent. Developer $20/mo, Startup $99/mo[^browserbase-pricing] |
| LLM | Your provider's token price, or $0 with your own local model | Same, or Gateway at provider price with no markup[^stagehand-models]. Free tier includes $5 in tokens[^browserbase-pricing] |
| Repeat Stagehand calls | Every instruction call runs inference[^stagehand-caching] | Cache hits make no LLM call[^stagehand-caching] |

# Security

Every page is untrusted input to the model, so a browsing agent is exposed to [goal hijack](/ai-engineering/security.md#risks-owasp-agentic-top-10) through prompt injection. Anthropic warns that instructions on webpages or in images can override your instructions.[^claude-computer-use] It recommends a dedicated VM or container with minimal privileges, no access to sensitive data or logins, a domain allowlist, and human confirmation of consequential actions.[^claude-computer-use] See [Agent Sandboxes](/ai-engineering/harness/sandboxes.md) for the isolation side.

[^playwright-intro]: Playwright docs, read 2026-11-04.
[^playwright-locators]: Playwright locators docs, read 2026-11-04.
[^playwright-aria]: Playwright ARIA snapshot docs, read 2026-11-04.
[^playwright-repo]: microsoft/playwright license from the GitHub API, read 2026-11-04.
[^playwright-mcp]: microsoft/playwright-mcp README, read 2026-11-04.
[^stagehand-quickstart]: Stagehand v4 quickstart, read 2026-11-04.
[^stagehand-act]: Stagehand v4 act docs, read 2026-11-04.
[^stagehand-extract]: Stagehand v4 extract docs, read 2026-11-04.
[^stagehand-models]: Stagehand v4 models configuration, read 2026-11-04.
[^stagehand-browser]: Stagehand v4 browser configuration, read 2026-11-04.
[^stagehand-caching]: Stagehand v4 caching guide, read 2026-11-04.
[^stagehand-repo]: browserbase/stagehand repository and license, read 2026-11-04.
[^browserbase-overview]: Browserbase docs, What is Browserbase?, read 2026-11-04.
[^browserbase-sessions]: Browserbase docs, create a browser session, read 2026-11-04.
[^browserbase-playwright]: Browserbase Playwright quickstart, read 2026-11-04.
[^browserbase-contexts]: Browserbase contexts docs, read 2026-11-04.
[^browserbase-captcha]: Browserbase CAPTCHA solving docs, read 2026-11-04.
[^browserbase-proxies]: Browserbase proxies docs, read 2026-11-04.
[^browserbase-pricing]: Browserbase pricing page, undated, read 2026-11-04.
[^claude-computer-use]: Anthropic computer use tool docs, read 2026-11-04.
[^chase-late-2026]: Harrison Chase, LangChain blog, 2026-11-02.
