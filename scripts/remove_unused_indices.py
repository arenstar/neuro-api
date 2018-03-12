import elasticsearch

elasticsearch_host = ['52.169.143.2:9200']
es = elasticsearch.Elasticsearch(elasticsearch_host)
indices = es.indices.get_alias("coining_latest_*")
available_coins = []
for item in indices:
    coin = item.split('coining_latest_')
    available_coins.append(coin[1])
print(available_coins)

available_coins = ['iota', 'siacoin', 'ethereumclassi', 'verge', 'digibyte', 'ripple', 'zcash', 'bitcoin', 'litecoin', 'wave', 'monacoin', 'ethereum', 'strati', 'komodo', 'ark', 'monero', 'qtum', 'decred', 'bitshare', 'nxt', 'golem', 'vertcoin', 'veritaseum', 'dash', 'ardor', 'nem', 'lisk', 'reddcoin', 'stellar']

indices = es.indices.get_alias("coinmarketcap_*")
for indice in indices:
    coin = indice.split('coinmarketcap_')[1]
    if not coin in available_coins:
        print(indice)
        es.indices.delete(index=indice, ignore=[400, 404])
