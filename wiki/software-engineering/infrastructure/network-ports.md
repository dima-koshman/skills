---
type: Concept
title: Well-Known Ports (22, 80, 443)
aliases:
- Network Ports
- Privileged Ports
- Port Conventions
description: Why ports 22, 80 and 443 matter beyond convention. Covers privileged ports, client defaults, browser
  port blocking, firewalls, and protocols that need a fixed port, plus what this means for a Runpod Pod.
tags:
- software-engineering
- infrastructure
- networking
parent: /software-engineering/infrastructure.md
status: draft
sources:
- id: rfc6335
  resource: https://www.rfc-editor.org/rfc/rfc6335
  title: 'RFC 6335: IANA Procedures for the Management of the Service Name and Transport Protocol Port Number Registry'
  author: IETF
- id: linux-ip7
  resource: https://man7.org/linux/man-pages/man7/ip.7.html
  title: ip(7), Linux manual page
  author: Linux man-pages project
- id: linux-ip-sysctl
  resource: https://docs.kernel.org/networking/ip-sysctl.html
  title: IP Sysctl
  author: Linux kernel documentation
- id: whatwg-fetch
  resource: https://fetch.spec.whatwg.org/#port-blocking
  title: 'Fetch Standard, section 2.9: Port blocking'
  author: WHATWG
- id: letsencrypt-challenges
  resource: https://letsencrypt.org/docs/challenge-types/
  title: Challenge Types
  author: Let's Encrypt
- id: rfc9114
  resource: https://www.rfc-editor.org/rfc/rfc9114
  title: 'RFC 9114: HTTP/3'
  author: IETF
- id: runpod-ports
  resource: https://docs.runpod.io/pods/configuration/expose-ports
  title: Expose ports
  author: Runpod
generated:
  by: claude-code/claude-opus-5-5
  at: '2026-11-17T17:45:00+04:00'
---

Nothing in TCP makes a port special. The protocol is decided by the bytes the two ends exchange, so sshd or nginx can
listen on any port. What makes 22, 80 and 443 special is everything around the server. Even the port registry warns
that "the assumption that a particular port number necessarily implies a particular service may become less
true."[^rfc6335]

# Port ranges

IANA splits port numbers into three ranges:[^rfc6335]

| Range | Name | Assigned |
| --- | --- | --- |
| 0–1023 | System Ports (Well Known Ports) | By IANA |
| 1024–49151 | User Ports (Registered Ports) | By IANA |
| 49152–65535 | Dynamic Ports (Private or Ephemeral Ports) | Never |

# What actually depends on the number

1. **Privileged ports.** On Linux, ports below 1024 are privileged. Only a process with `CAP_NET_BIND_SERVICE`
   (usually root) may bind to them.[^linux-ip7] The `net.ipv4.ip_unprivileged_port_start` sysctl moves that line per
   network namespace; it defaults to 1024, and 0 disables privileged ports.[^linux-ip-sysctl] As root, this doesn't
   affect you.
2. **Client defaults.** `https://host` means 443 and `ssh host` means 22. Any other port has to be written
   everywhere: `:8443` in URLs, `-p 2222` or `Port` in the SSH config.
3. **Browser port blocking.** The Fetch standard blocks HTTP(S) requests to any "bad port".[^whatwg-fetch] The list
   includes 22 (ssh), 25 (smtp), 6000 (x11) and about 80 others, but not 80 or 443. So HTTP on port 22 fails in a
   browser (Chrome shows `ERR_UNSAFE_PORT`) while curl works. A full swap of SSH and HTTP ports is not possible for
   browser traffic.
4. **Firewalls and proxies.** This is the biggest one, and it is our own analysis without a single source. Office,
   hotel and guest networks often allow only 80 and 443 outbound.
   - SSH on 443 gets past a firewall that only checks port numbers.
   - It fails behind a proxy that inspects TLS or allows only HTTP, because SSH isn't TLS.
   - Non-HTTP traffic on 80 is worse, since transparent HTTP proxies break it.
   - The fix is to wrap the protocol in TLS or WebSocket, or to use an outbound tunnel.
5. **Protocols that require a fixed port.**
   - Let's Encrypt HTTP-01 challenges "can only be done on port 80"; TLS-ALPN-01 runs on 443.[^letsencrypt-challenges]
   - HTTP/3 has no fixed port: "Servers MAY serve HTTP/3 on any UDP port". Clients find it through the URI or an
     `Alt-Svc` header, which always names a port.[^rfc9114] UDP 443 is common practice, not a rule.

# Example: a Runpod Pod

- **Direct TCP.** A Pod's internal port such as 22 is mapped to a public IP and an assigned external port, for
  example `213.173.109.39:13007 -> :22`. The mapping changes whenever the Pod resets.[^runpod-ports] Running sshd on
  443 inside the Pod doesn't change the external port, and the external port is what a strict network blocks. Port
  numbers above 70000 in the config ask Runpod for matching internal and external ports.[^runpod-ports]
- **HTTP proxy.** `https://[POD_ID]-[INTERNAL_PORT].proxy.runpod.net` goes through Cloudflare and is always HTTPS on
  the outside. Cloudflare closes connections after 100 seconds with a 524 error. Runpod's advice: "Use HTTP proxy for
  web services and TCP for everything else."[^runpod-ports]
- **Pods don't support UDP.**[^runpod-ports]
- **Blocked networks.** An outbound tunnel, such as VS Code Remote Tunnels, needs no inbound port on either side. It
  is the reliable choice when direct SSH is blocked (our own analysis).

[^rfc6335]: RFC 6335, sections 3 and 6.
[^linux-ip7]: ip(7), DESCRIPTION and ERRORS (EACCES).
[^linux-ip-sysctl]: Linux kernel docs, `ip_unprivileged_port_start`.
[^whatwg-fetch]: WHATWG Fetch Standard, section 2.9 "Port blocking".
[^letsencrypt-challenges]: Let's Encrypt, "Challenge Types".
[^rfc9114]: RFC 9114, sections 3.1 and 3.1.1.
[^runpod-ports]: Runpod docs, "Expose ports".
