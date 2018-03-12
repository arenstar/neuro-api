from datetime import datetime
import elasticsearch
import json
import falcon
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend

elasticsearch_host = ['52.169.143.2:9200']

httpauth = {}
httpauth['rainmaker'] = "bn8p#s2sYkc"

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

class LatestCoinResource:
    def on_get(self, req, resp, coin):

        if req.context['user']['username'] not in httpauth:
            resp.status = falcon.HTTP_401
            return
        if req.context['user']['password'] != httpauth[req.context['user']['username']]:
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

class LatestAllResource:
    def on_get(self, req, resp):

        if req.context['user']['username'] not in httpauth:
            resp.status = falcon.HTTP_401
            return
        if req.context['user']['password'] != httpauth[req.context['user']['username']]:
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


user_loader = lambda username, password: { 'username': username , 'password': password }
auth_backend = BasicAuthBackend(user_loader)

auth_middleware = FalconAuthMiddleware(auth_backend,exempt_routes=['/api/status'])
api = falcon.API(middleware=[auth_middleware])
api.add_route('/api/status', StatusResource())
api.add_route('/api/latest/all', LatestAllResource())
api.add_route('/api/latest/{coin}', LatestCoinResource())
