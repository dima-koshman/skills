# htmx

Small, dependency-free JavaScript library that lets any HTML element issue HTTP requests and swap the returned HTML into the page — interactivity without a frontend framework.

Reference: <https://htmx.org>

Note dated: 2026-10-03. htmx 4.0 is released but not yet marked `latest` on npm
(planned for 2027, details at <https://four.htmx.org>); 2.0.x is the stable line.
2.x dropped IE support, and the 1.x line is kept for IE.

htmx removes the limits plain HTML puts on interactivity: only `<a>` and `<form>`
make requests, only `click` and `submit` trigger them, only GET and POST are
available, and every response replaces the whole page. With htmx, attributes
declare all four on any element:

| Attribute | Declares |
| --- | --- |
| `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete` | Which request to send |
| `hx-trigger` | Which event sends it, e.g. `keyup changed delay:300ms`, `revealed`, `every 2s` |
| `hx-target` | Which element receives the response (CSS selector) |
| `hx-swap` | How it is inserted, e.g. `innerHTML`, `outerHTML`, `beforeend` |

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"></script>

<input name="q" hx-get="/search" hx-trigger="keyup changed delay:300ms"
       hx-target="#results">
<ul id="results"></ul>
```

The server answers `/search` with an HTML fragment (`<li>…</li>`), not JSON.

## The hypermedia model

The server renders HTML and owns state; the browser shows what it is sent.
There is no client-side model, JSON API, or build step. That is the opposite
of the SPA model, where the server is a JSON API and a React or Vue client
renders the UI. Any backend that renders templates works, for example FastAPI
or Django with Jinja templates. WebSockets, Server-Sent Events, and CSS
transitions are also declared through attributes.

## Where it fits

- **Good fit:** CRUD apps, admin panels, internal tools, dashboards, forms, search-as-you-type,
  infinite scroll, polling status pages. Mostly server-rendered apps that need some interactivity
  without the cost of a second (JavaScript) application and its build chain.
- **Poor fit:** UIs with rich client-side state or offline use, such as editors, canvases, or
  heavy drag-and-drop, and products that need a JSON API for mobile or third-party clients
  anyway. There the HTML endpoints would be a second interface to maintain.
- **Trade-offs:** every interaction is a server round trip, so latency matters more than in an
  SPA. Templates become the UI contract, so endpoints that return fragments are coupled to the
  page structure. Small client-side behavior is usually paired with a tiny script layer such as
  Alpine.js rather than a framework.

## Resources

- [Documentation](https://htmx.org/docs/)
- [Attribute reference](https://htmx.org/reference/)
- [Examples](https://htmx.org/examples/) — common UI patterns implemented with htmx
- [Essays](https://htmx.org/essays/) — the hypermedia rationale, including when *not* to use it
- [Hypermedia Systems](https://hypermedia.systems/) — the authors' book on the approach
