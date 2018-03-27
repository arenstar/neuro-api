import requests
import json
import sys
import elasticsearch
import schedule

elasticsearch_host = ['52.169.143.2:9200']

available_coins = ['stellar','monacoin','cardano','bitcoindark','digibyte','litecoin','bitcoin','monero','ethereum-classic','veritaseum','bitshares','siacoin','reddcoin','peercoin','decred','ethereum','golem-network-tokens','chaincoin','dash','verge','ripple','vertcoin','nem','waves','ardor','zcash','lisk','qtum','nxt', 'ark', 'einsteinium', 'iota', 'stratis', 'komodo']

def scrape():

    es = elasticsearch.Elasticsearch(elasticsearch_host)

    response = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=0')
    json_data = json.loads(response.text)

    for coin in json_data:
        result = {}
        if coin['id'] in available_coins:
            result['id'] = coin['last_updated']
            result['index'] = coin['id']
            ####
            result['last_updated'] = str(coin['last_updated'])
            ####
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
            print(es.index(index="new_coinmarketcap_"+str(result['index']), doc_type="coinmarketcap", id=result['id'], body=result))


schedule.every(1).minutes.do(scrape)

while True:
    schedule.run_pending()
