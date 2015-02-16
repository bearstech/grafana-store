from flask import Flask, abort, Response, request, jsonify
import os
import os.path
import json
from glob import glob
import codecs

from addict import Dict

class GrafanaStore(Flask):

    def __init__(self, *args):
        if not os.path.exists('data'):
            os.mkdir('data')
        super(GrafanaStore, self).__init__(*args)


app = GrafanaStore(__name__)


@app.route('/grafana-dash/dashboard/<dashboard>', methods=['GET', 'PUT', 'DELETE'])
def dashboard(dashboard):
    path = 'data/%s.json' % dashboard
    if request.method == 'GET':
        if not os.path.exists(path):
            abort(404)
        return Response(open(path, 'r').xreadlines(),
                        mimetype='application/json')
    elif request.method == 'PUT':
        with open(path, 'w') as f:
            # Check json validity
            json.dump(json.loads(request.get_data()), f)
        return jsonify(ok=True), 201
    else:
        abort(400)


@app.route('/grafana-dash/dashboard/_search', methods=['POST'])
def search():
    """
    {"query":{"query_string":{"query":"title:*"}},"facets":{"tags":{"terms":{"field":"tags","order":"term","size":50}}},"size":20,"sort":["_uid"]}
    """
    q = Dict(json.loads(request.get_data()))
    if not q.query.query_string.query == "title:*":
        return jsonify([])
    else:
        hits = []
        for p in glob('data/*.json'):
            raw = codecs.open(p, 'r', 'utf8').read()
            j = Dict(json.loads(raw))
            d = Dict()
            d._index = 'grafana-dash'
            d._type = 'dashboard'
            d._score = None
            d._id = j.title
            d._source.title = j.title
            d._source.user = "guest"
            d._source.group = "guest"
            d._source.tags = j.tags
            d._source.dashboard = raw

            hits.append(d)
        r = Dict()
        r.hits.total = len(hits)
        r.hits.hits = hits
        r.facets.tags._type = "terms"
        r.facets.tags.terms = []
        r.facets.tags.total = 0
        r.facets.tags.other = 0
        print r
        return jsonify(r, mimetype='application/json')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
