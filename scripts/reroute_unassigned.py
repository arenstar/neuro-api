# example python script

# pip install requests before using requests
import requests
import json

HOSTNAME="52.169.143.2" # hostname
PORT=9200 # port number
NODE_NAME="node-1" # node to reroute to 

def reroute(index, shard):
  payload = { "commands": [{ "allocate": { "index": index, "shard": shard, "node": NODE_NAME, "allow_primary": 1 } }] }
  res = requests.post("http://" + HOSTNAME + ":" + str(PORT) + "/_cluster/reroute", data=json.dumps(payload))
  print(res.text)
  pass

res = requests.post("http://" + HOSTNAME + ":" + str(PORT) + "/_flush/synced")
j = res.json()

for field in j:
  if j[field]["failed"] != 0 and field != "_shards":
    for item in j[field]["failures"]:
      reroute(field, item["shard"])
