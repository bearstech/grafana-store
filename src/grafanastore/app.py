from flask import Flask, abort, Response, request, jsonify
import os
import os.path
import json


class GrafanaStore(Flask):

    def __init__(self, *args):
        if not os.path.exists('data'):
            os.mkdir('data')
        super(GrafanaStore, self).__init__(*args)


app = GrafanaStore(__name__)


@app.route('/dashboard/<dashboard>', methods=['GET', 'PUT'])
def bashboard(dashboard):
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

if __name__ == "__main__":
    app.debug = True
    app.run()
