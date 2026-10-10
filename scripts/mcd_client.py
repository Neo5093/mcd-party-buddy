"""麦当劳 MCP 客户端（纯标准库，零依赖）。

Token 只从环境变量 MCD_MCP_TOKEN 读取，请勿写入代码或提交仓库。
协议：Streamable HTTP —— POST JSON-RPC，响应可能是 application/json 或 text/event-stream。
"""
import json
import os
import urllib.request

BASE_URL = "https://mcp.mcd.cn"
PROTOCOL_VERSION = "2025-03-26"


class McdClient:
    def __init__(self, token=None, base_url=BASE_URL):
        self.token = token or os.environ.get("MCD_MCP_TOKEN", "")
        if not self.token:
            raise SystemExit("缺少 MCD_MCP_TOKEN 环境变量，请先申请：https://open.mcd.cn/mcp")
        self.base_url = base_url
        self.session_id = None
        self._id = 0
        self._initialize()

    def _post(self, payload):
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.token}",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.base_url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            raw = resp.read().decode("utf-8")
        # SSE 响应：取 data: 行中的 JSON
        if raw.lstrip().startswith("event:") or "\ndata:" in raw:
            for line in raw.splitlines():
                if line.startswith("data:"):
                    return json.loads(line[5:].strip())
            raise RuntimeError(f"SSE 响应中无 data 行: {raw[:200]}")
        return json.loads(raw)

    def _rpc(self, method, params=None):
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            payload["params"] = params
        result = self._post(payload)
        if "error" in result:
            raise RuntimeError(f"MCP 错误: {result['error']}")
        return result.get("result", {})

    def _initialize(self):
        self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "party-buddy", "version": "0.1.0"},
        })
        # initialized 通知（无 id）
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, tool, arguments=None):
        """调用 MCP 工具，返回 content[0].text 解析后的 JSON（或原始文本）。"""
        result = self._rpc("tools/call", {"name": tool, "arguments": arguments or {}})
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            text = content[0]["text"]
            try:
                return json.loads(text)
            except (json.JSONDecodeError, ValueError):
                return text
        return result
