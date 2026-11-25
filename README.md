# neckrez-mcp

[![tests](https://github.com/Sauberr/neckrez-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/Sauberr/neckrez-mcp/actions/workflows/test.yml)

MCP server for [Neckrez](https://neckrez.tech): let an AI assistant (Claude, Cursor, VS Code, any MCP client) list plans and prices, get a quote, create a VPS, dedicated CPU, GPU or bare metal server with your SSH key, and reboot, back up or destroy it from the chat.

Neckrez is a crypto-paid cloud host: sign up with an email only (no ID, no card, no KYC), top up a prepaid balance with Bitcoin, USDT, Monero or 300+ other coins, and pay by the hour. Servers run on Vultr, DigitalOcean, Linode and Hetzner.

This is a **remote** server. There is nothing to install: the MCP endpoint is hosted by Neckrez.

| | |
|---|---|
| Endpoint | `https://neckrez.tech/api/mcp` |
| Transport | Streamable HTTP (stateless, `POST`, JSON responses) |
| Auth | `Authorization: Bearer nek_...` (an API key from [your dashboard](https://neckrez.tech/dashboard/api-keys)) |
| Docs | https://neckrez.tech/docs/mcp |

`initialize` and `tools/list` work without a key, so clients and directories can see the tools. Calling a tool needs a key.

## Connect

Create an API key at [neckrez.tech/dashboard/api-keys](https://neckrez.tech/dashboard/api-keys). Pick its permissions: `read` (always on), `deploy`, `destroy`, `support`, `billing`. Start with only `read` if you only want the assistant to look.

**Claude Code**

```bash
claude mcp add --transport http neckrez https://neckrez.tech/api/mcp \
  --header "Authorization: Bearer nek_your_key"
```

**Cursor** (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "neckrez": {
      "url": "https://neckrez.tech/api/mcp",
      "headers": { "Authorization": "Bearer nek_your_key" }
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`, asks for the key once)

```json
{
  "inputs": [
    { "type": "promptString", "id": "neckrez-key", "description": "Neckrez API key", "password": true }
  ],
  "servers": {
    "neckrez": {
      "type": "http",
      "url": "https://neckrez.tech/api/mcp",
      "headers": { "Authorization": "Bearer ${input:neckrez-key}" }
    }
  }
}
```

**Claude Desktop** (`claude_desktop_config.json`, needs Node.js for the `mcp-remote` bridge)

```json
{
  "mcpServers": {
    "neckrez": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://neckrez.tech/api/mcp", "--header", "Authorization:${NECKREZ_AUTH}"],
      "env": { "NECKREZ_AUTH": "Bearer nek_your_key" }
    }
  }
}
```

## Try it

- "Spin up a small Ubuntu server in Frankfurt for an hour. Here is my key: ssh-ed25519 AAAA..."
- "What is the cheapest GPU I can get in Europe right now, and how long does my balance last with it?"
- "List my servers and destroy the ones named test-1 and test-2."
- "My balance is low: prepare a $20 top-up in USDT on BSC."

## Tools

| Tool | What it does | Key permission |
|---|---|---|
| `get_account` | Balance, hourly spend, how long the balance lasts, servers against the limit | read |
| `list_options` | Plans with vCPU, RAM, disk, traffic, GPU, prices and locations; filters | read |
| `list_locations` | Locations with codes, cities, countries | read |
| `list_os` | OS images and one-click apps | read |
| `quote` | Price of an order and whether the balance covers it | read |
| `create_server` | Create 1 to 3 servers (OS or app) | deploy |
| `list_servers`, `get_server` | Servers with status, IPs and an ssh command | read |
| `server_power` | Reboot, stop or start | deploy |
| `get_root_password` | Login and root password | deploy |
| `change_ip` | New public IPv4 (needs `confirm` and the exact name) | deploy |
| `destroy_server` | Delete a server (needs `confirm` and the exact name) | destroy |
| `get_rdns`, `set_rdns` | Reverse DNS (PTR) records | read / deploy |
| `list_backups`, `create_backup`, `restore_backup`, `delete_backup` | Snapshots kept 7 days | read / deploy / destroy |
| `billing_history` | Recent top-ups and charges | read |
| `list_currencies` | Coins the balance can be topped up with, minimums and VAT | read |
| `top_up` | Create a crypto payment for you to pay: address, exact amount, network, deadline | billing |
| `list_deposits`, `deposit_status` | Your top-ups; a status check credits the balance once the payment is confirmed | read |
| `support_read`, `support_send` | Read the support chat; write to support on your behalf (marked as sent by an AI assistant, at most 10 an hour) | support |

## Money and safety

- One `create_server` call makes at most 3 servers and at most **$1 per hour** in total unless the assistant passes a higher `max_hourly_usd`. Above that nothing is created and the tool returns the price, so the assistant has to ask you. `restore_backup` works the same way.
- `destroy_server`, `change_ip` and `delete_backup` need `confirm: true` and the exact server name (or backup label).
- Each tool needs one key permission: `read` for the read tools, `deploy` to create and change, `destroy` for `destroy_server` and `delete_backup`, `billing` for `top_up`, `support` for the support chat. A key without `destroy` is a good default for an assistant: it can build, and you delete from the dashboard.
- `top_up` only creates a payment request (an address and an exact amount). No money moves until you send the coins yourself; `deposit_status` shows when the balance is credited. It needs the `billing` permission. A stopped server is still billed; billing stops when a server is destroyed.
- Give the assistant your SSH public key. Without one the root password is available in the dashboard or through `get_root_password`, and then it stays in the chat history.
- Requests share the API limit of 60 per minute per key.

Neckrez is a reseller, so the underlying provider's network and rules apply. Top-ups are not refundable and there is no SLA. See the [Terms](https://neckrez.tech/legal/terms).

## Without an MCP client

`examples/list_plans.py` calls the server with plain HTTP (standard library only, read-only):

```bash
NECKREZ_API_KEY=nek_your_key python3 examples/list_plans.py gpu
```

## Tests

```bash
python -m unittest discover -s tests -v
```

`tests/test_manifest.py` checks `server.json` and this README offline. `tests/test_live.py` checks the hosted endpoint (handshake,
the tool list, that calls without a valid key are refused) without an API key, so nothing is created or charged; set
`NECKREZ_SKIP_LIVE=1` to skip it. CI runs both on every push and once a day. Changes: [CHANGELOG.md](CHANGELOG.md).

## Related

- REST API and OpenAPI 3.1: https://neckrez.tech/docs/api · https://neckrez.tech/api/v1/openapi.json
- Command-line client: https://github.com/Sauberr/neckrez-cli
- `llms.txt` for AI agents: https://neckrez.tech/llms.txt
- Support: support@neckrez.tech

## License

MIT, see [LICENSE](LICENSE). The hosted service is governed by the Neckrez Terms.
