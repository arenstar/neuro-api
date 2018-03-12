from datetime import datetime
import elasticsearch
import json
import falcon
import requests
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend

elasticsearch_host = ['127.0.0.1:9200']

httpauth = {}
httpauth['user1'] = "password"
httpauth['user2'] = "password"

class StatusResource:
    def on_get(self, req, resp):

        try:
            es = elasticsearch.Elasticsearch(elasticsearch_host)
            health = es.cluster.health()
            if health['status'] != 'green' or health['status'] != 'yellow':
                resp.status = falcon.HTTP_500
            resp.body = json.dumps(health['status'], ensure_ascii=False)
            resp.status = falcon.HTTP_200
        except elasticsearch.ElasticsearchException:
            resp.media = "ElasticSearch ConnectionRefusedError"
            resp.status = falcon.HTTP_500

class LatestAllResource:
    def on_get(self, req, resp):

        if req.context['user']['username'] not in httpauth:
            resp.status = falcon.HTTP_401
            return
        if req.context['user']['password'] != httpauth[req.context['user']['password']]:
            resp.status = falcon.HTTP_401
            return

        try:
            es = elasticsearch.Elasticsearch(elasticsearch_host)
            indices = es.indices.get_alias("coining_latest_*")
            available_coins = []
            for item in indices:
                coin = item.split('coining_latest_')
                available_coins.append(coin[1])

            doc = {
                'available_coins': available_coins
            }
            resp.body = json.dumps(doc, ensure_ascii=False)
            resp.status = falcon.HTTP_200
 
        except elasticsearch.ElasticsearchException:
            resp.media = "ElasticSearch ConnectionRefusedError"
            resp.status = falcon.HTTP_500

class CoinmarketcapCoinResource:

    def on_get(self, req, resp, coin):

        es = elasticsearch.Elasticsearch(elasticsearch_host)
        available_coins = ['iota', 'siacoin', 'ethereumclassi', 'verge', 'digibyte', 'ripple', 'zcash', 'bitcoin', 'litecoin', 'wave', 'monacoin', 'ethereum', 'strati', 'komodo', 'ark', 'monero', 'qtum', 'decred', 'bitshare', 'nxt', 'golem', 'vertcoin', 'veritaseum', 'dash', 'ardor', 'nem', 'lisk', 'reddcoin', 'stellar']

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
        result = es.search(index="coinmarketcap_"+str(coin), doc_type="coinmarketcap", body=query)
        #result = es.search(index="coinmarketcap_"+str(coin), doc_type="coinmarketcap")
        print(result)
        resp.body = json.dumps(result, ensure_ascii=False)
        resp.status = falcon.HTTP_200

class CoinmarketcapUpdateResource:

    def on_get(self, req, resp):

        es = elasticsearch.Elasticsearch(elasticsearch_host)

        available_coins = ['iota', 'siacoin', 'ethereumclassi', 'verge', 'digibyte', 'ripple', 'zcash', 'bitcoin', 'litecoin', 'wave', 'monacoin', 'ethereum', 'strati', 'komodo', 'ark', 'monero', 'qtum', 'decred', 'bitshare', 'nxt', 'golem', 'vertcoin', 'veritaseum', 'dash', 'ardor', 'nem', 'lisk', 'reddcoin', 'stellar']

        response = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=0')
        json_data = json.loads(response.text)

        for coin in json_data:
            result = {}
            if coin['id'] in available_coins:
                result['id'] = coin['id']
                result['last_updated'] = datetime.fromtimestamp(int(coin['last_updated'])).isoformat()
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
                print(es.index(index="coinmarketcap_"+str(result['id']), doc_type="coinmarketcap", id=result['last_updated'], body=result))
        resp.status = falcon.HTTP_200

class LatestCoinResource:
    def on_get(self, req, resp, coin):

        if req.context['user']['username'] not in httpauth:
            resp.status = falcon.HTTP_401
            return
        if req.context['user']['password'] != httpauth[req.context['user']['password']]:
            resp.status = falcon.HTTP_401
            return
            
        try:
            es = elasticsearch.Elasticsearch(elasticsearch_host)
            result = es.search(index='coining_latest_%s' % (coin), doc_type="coining_latest")
        
            if len(result['hits']['hits']) != 1:
                resp.status = falcon.HTTP_500

            resp.body = json.dumps(result['hits']['hits'][0]['_source'], ensure_ascii=False)
            resp.status = falcon.HTTP_200

        except elasticsearch.ElasticsearchException:
            resp.media = "ElasticSearch ConnectionRefusedError"
            resp.status = falcon.HTTP_500


    def on_post(self, req, resp, decision, coin, last_upd):
        print("storing decision for", coin)
        doc_type = "coining"
        index = doc_type + "_" + coin
        id = int(last_upd.tolist() / 1e9)

        latest_doc_type = "coining_latest"
        latest_index = latest_doc_type + "_" + curr

        last_upd = datetime.datetime.fromtimestamp(id)
        body = {
            "currency": curr,
            "last_updated": last_upd,
            **decision
        }
        d = dict(index=index, doc_type=doc_type, id=id, body=body)
        d_latest = dict(index=latest_index, doc_type=latest_doc_type, id=1, body=body)
        print(d)
        print(d_latest)
        #self.es.index(**d)
        #self.es.index(**d_latest)
        resp.status = falcon.HTTP_200

user_loader = lambda username, password: { 'username': username , 'password': password }
auth_backend = BasicAuthBackend(user_loader)

auth_middleware = FalconAuthMiddleware(auth_backend,exempt_routes=['/api/status'])
api = falcon.API(middleware=[auth_middleware])
api.add_route('/api/status', StatusResource())
api.add_route('/api/latest/all', LatestAllResource())

# Get Latest / Post Latest from AI
api.add_route('/api/latest/{coin}', LatestCoinResource())

# Get Latest / Post Latest from coinmarketcap
api.add_route('/api/coinmarketcap/{coin}', CoinmarketcapCoinResource())
api.add_route('/api/coinmarketcap/update', CoinmarketcapUpdateResource())

