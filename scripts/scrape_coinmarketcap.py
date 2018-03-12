import requests
import json
import sys
import elasticsearch

elasticsearch_host = ['52.169.143.2:9200']
es = elasticsearch.Elasticsearch(elasticsearch_host)

available_coins = ['iota', 'siacoin', 'ethereumclassi', 'verge', 'digibyte', 'ripple', 'zcash', 'bitcoin', 'litecoin', 'wave', 'monacoin', 'ethereum', 'strati', 'komodo', 'ark', 'monero', 'qtum', 'decred', 'bitshare', 'nxt', 'golem', 'vertcoin', 'veritaseum', 'dash', 'ardor', 'nem', 'lisk', 'reddcoin', 'stellar']

response = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=10')
json_data = json.loads(response.text)

for coin in json_data:
    result = {}
    if coin['id'] in available_coins:
        result['id'] = coin['id']
        result['last_updated'] = str(coin['last_updated'])
        result['rank'] = int(coin['rank'])
        result['price_usd'] = float(coin['price_usd'])
        result['price_btc'] = float(coin['price_btc'])
        result['24h_volume_usd'] = float(coin['24h_volume_usd'])
        result['market_cap_usd'] = float(coin['market_cap_usd'])
        result['available_supply'] = float(coin['available_supply'])
        result['total_supply'] = float(coin['total_supply'])
        result['max_supply'] = coin['max_supply']
        result['percent_change_1h'] = coin['percent_change_1h']
        result['percent_change_24h'] = coin['percent_change_24h']
        result['percent_change_7d'] = coin['percent_change_7d']
        if coin['id'] == 'bitcoin':
            print(result['last_updated'])
            print(es.index(index="coinmarketcap_"+str(result['id']), doc_type="coinmarketcap", id=result['last_updated'], body=result))

            query = json.dumps({
              "query": {
                "range": {
                     "last_updated": {
                         "gte": "now-25h",
                          "lt": "now"
                     }
                 }
              },
              "sort": [{"last_updated": {"order": "asc"}}],
              "size": 1500
            })
            #result = self.es.search(index="coinmarketcap_"+coin, doc_type="coinmarketcap", body=query)
            print(es.search(index="coinmarketcap_"+str(result['id']), doc_type="coinmarketcap", body=query))
            

