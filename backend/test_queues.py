import os
import json
from mikrotik_client import load_config, RouterOSApi

cfg = load_config()
host = cfg.get("mikrotik_host", "")
port = cfg.get("mikrotik_port", 8520)
username = cfg.get("mikrotik_username", "")
password = cfg.get("mikrotik_password", "")
use_ssl = cfg.get("mikrotik_use_ssl", False)

api = RouterOSApi(host, port, username, password, use_ssl)
api.connect()

queues_reply = api.talk(["/queue/simple/print"])
api.close()

queues = []
for sentence in queues_reply:
    if sentence[0] == "!re":
        item = {}
        for word in sentence[1:]:
            if word.startswith("="):
                parts = word[1:].split("=", 1)
                if len(parts) == 2:
                    item[parts[0]] = parts[1]
        queues.append(item)

print(f"Found {len(queues)} simple queues.")
for q in queues[:15]:
    print(f"  Queue Name: {q.get('name')}, bytes: {q.get('bytes')}")
