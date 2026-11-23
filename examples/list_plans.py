#!/usr/bin/env python3
"""Call the Neckrez MCP server without an MCP client: list the cheapest plans of a product line.

    NECKREZ_API_KEY=nek_... python3 examples/list_plans.py gpu

Standard library only. Read-only: it creates nothing.
"""

import json
import os
import sys
import urllib.request

URL = os.environ.get("NECKREZ_MCP_URL", "https://neckrez.tech/api/mcp")


def call(tool, arguments):
    key = os.environ.get("NECKREZ_API_KEY")
    if not key:
        sys.exit("Set NECKREZ_API_KEY (create a key at https://neckrez.tech/dashboard/api-keys)")
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": arguments}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if "error" in res:
        sys.exit(res["error"]["message"])
    if res["result"].get("isError"):
        sys.exit(res["result"]["content"][0]["text"])
    return res["result"]["structuredContent"]


if __name__ == "__main__":
    product = sys.argv[1] if len(sys.argv) > 1 else "vps"
    data = call("list_options", {"product": product, "limit": 10})
    print(f"{data['count']} {product} plans, cheapest first:")
    for p in data["plans"]:
        gpu = f" {p['gpu_type']}" if p.get("gpu_type") else ""
        print(f"  {p['provider']:<13}{p['id']:<34}{p['vcpu']} vCPU {p['ram_gb']} GB{gpu}  ${p['price_month']}/mo  ${p['price_hour']}/h")
