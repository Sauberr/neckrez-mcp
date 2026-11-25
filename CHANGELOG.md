# Changelog

## 1.4.0 — 2026-11-26
- OAuth 2.1 sign-in at `https://neckrez.tech/mcp`: Claude, ChatGPT and Claude Code connect without an API key; the user picks permissions and an hourly spending cap, and can disconnect the app from the dashboard.

## 1.3.0 — 2026-11-25
- New tool: `reset_root_password` (a new password without a reinstall, through the server's recovery key).

## 1.2.0 — 2026-11-25
- API keys carry permissions (read, deploy, destroy, support, billing); every tool checks the one it needs and says which is missing.
- New tools: `support_read`, `support_send`.

## 1.1.0 — 2026-11-24
- New tools: `list_currencies`, `top_up` (creates a crypto payment request for the user to pay), `list_deposits`, `deposit_status`.

## 1.0.0 — 2026-11-23
- Hosted MCP server at `https://neckrez.tech/api/mcp` (Streamable HTTP, Bearer API key).
- 19 tools: account, plans and prices, locations, OS and apps, quotes, create/list/get servers, power actions, root password,
  new IPv4, destroy, reverse DNS, backups (list, create, restore, delete), billing history.
- Safety rails: at most 3 servers and $1/h per create call unless `max_hourly_usd` is raised; `confirm` plus the exact name
  for destroy, IP change and backup deletion; read-only keys limited to read tools.
- Registry manifest (`server.json`), Glama maintainer file, offline and live tests, daily CI check of the endpoint.
