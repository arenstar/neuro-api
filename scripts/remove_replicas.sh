#!/bin/bash

curl -XPUT 'http://52.169.143.2:9200/_settings?pretty' -H 'Content-Type: application/json' -d'
{
    "index" : {
        "number_of_replicas" : 0
    }
}
'
