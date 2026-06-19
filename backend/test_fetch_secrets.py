import os
import json
from mikrotik_client import load_config, RouterOSApi

cfg = load_config()
host = cfg.get("mikrotik_host", "")
port = cfg.get("mikrotik_port", 8520)
username = cfg.get("mikrotik_username", "")
password = cfg.get("mikrotik_password", "")
use_ssl = cfg.get("mikrotik_use_ssl", False)

print(f"Connecting to Mikrotik at {host}:{port} with user {username}...")
api = RouterOSApi(host, port, username, password, use_ssl)
api.connect()

secrets_reply = api.talk(["/ppp/secret/print"])
api.close()

secrets = []
for sentence in secrets_reply:
    if sentence[0] == "!re":
        item = {}
        for word in sentence[1:]:
            if word.startswith("="):
                parts = word[1:].split("=", 1)
                if len(parts) == 2:
                    item[parts[0]] = parts[1]
        secrets.append(item)

print(f"Found {len(secrets)} secrets.")
for s in secrets[:10]:
    print(f"  User: {s.get('name')}, Comment: {s.get('comment', 'None')}")
