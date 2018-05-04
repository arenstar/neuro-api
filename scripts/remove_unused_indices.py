import elasticsearch

elasticsearch_host = ['52.169.143.2:9200']
es = elasticsearch.Elasticsearch(elasticsearch_host)
indices = es.indices.get_alias("coining_latest_*")
available_coins = []
for item in indices:
    coin = item.split('coining_latest_')
    available_coins.append(coin[1])
print(available_coins)

available_coins = ['stellar','monacoin','cardano','bitcoindark','digibyte','litecoin','bitcoin','monero','ethereum-classic','veritaseum','bitshares','siacoin','reddcoin','peercoin','decred','ethereum','golem-network-tokens','chaincoin','dash','verge','ripple','vertcoin','nem','waves','ardor','zcash','lisk','qtum','nxt', 'ark', 'einsteinium', 'iota', 'stratis', 'komodo']

indices = es.indices.get_alias("new_coinmarketcap_*")
for indice in indices:
    coin = indice.split('new_coinmarketcap_')[1]
    if not coin in available_coins:
        print(indice)
        es.indices.delete(index=indice, ignore=[400, 404])

es.indices.delete(index="new_coinmarketcap_ardor", ignore=[400, 404])
