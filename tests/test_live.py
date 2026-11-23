"""Live checks against the hosted endpoint: the MCP handshake, the tool list and auth.

No API key is used, so nothing is created or charged. Set NECKREZ_SKIP_LIVE=1 to skip
(for example offline), or NECKREZ_MCP_URL to point at another deployment.
"""

import json
import os
import unittest
import urllib.error
import urllib.request

URL = os.environ.get("NECKREZ_MCP_URL", "https://neckrez.tech/api/mcp")
EXPECTED_TOOLS = {
    "get_account", "list_options", "list_locations", "list_os", "quote", "create_server", "list_servers",
    "get_server", "server_power", "get_root_password", "change_ip", "destroy_server", "get_rdns", "set_rdns",
    "list_backups", "create_backup", "restore_backup", "delete_backup", "billing_history",
}
DESTRUCTIVE = {"destroy_server", "change_ip", "delete_backup"}


def rpc(method, params=None, msg_id=1, headers=None):
    body = {"jsonrpc": "2.0", "method": method, "params": params or {}}
    if msg_id is not None:
        body["id"] = msg_id
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
        "User-Agent": "neckrez-mcp-tests", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, json.loads(raw) if raw else None


@unittest.skipIf(os.environ.get("NECKREZ_SKIP_LIVE"), "live tests skipped")
class Live(unittest.TestCase):
    def test_initialize(self):
        status, res = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                         "clientInfo": {"name": "tests", "version": "1"}})
        self.assertEqual(status, 200)
        result = res["result"]
        self.assertEqual(result["serverInfo"]["name"], "neckrez")
        self.assertIn("tools", result["capabilities"])
        self.assertEqual(result["protocolVersion"], "2025-06-18")

    def test_notification_is_accepted(self):
        status, _ = rpc("notifications/initialized", msg_id=None)
        self.assertEqual(status, 202)

    def test_tool_list(self):
        status, res = rpc("tools/list")
        self.assertEqual(status, 200)
        tools = {t["name"]: t for t in res["result"]["tools"]}
        self.assertEqual(set(tools), EXPECTED_TOOLS)
        for name, t in tools.items():
            self.assertEqual(t["inputSchema"]["type"], "object", name)
            self.assertTrue(t["description"], name)
            self.assertEqual(t["annotations"]["destructiveHint"], name in DESTRUCTIVE, name)

    def test_tool_call_needs_a_key(self):
        status, res = rpc("tools/call", {"name": "get_account", "arguments": {}})
        self.assertEqual(status, 401)
        self.assertIn("API key", res["error"]["message"])

    def test_bad_key_is_rejected(self):
        status, _ = rpc("tools/call", {"name": "list_options", "arguments": {}},
                        headers={"Authorization": "Bearer nek_not_a_real_key"})
        self.assertEqual(status, 401)

    def test_unknown_method(self):
        status, res = rpc("does/not/exist")
        self.assertEqual(status, 200)
        self.assertEqual(res["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
