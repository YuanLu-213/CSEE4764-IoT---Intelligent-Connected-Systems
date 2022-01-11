from flask import Flask, render_template, Response
import queue
import json
import random
import time

app = Flask(__name__)
gps_data_q = queue.Queue()

@app.route("/")
def hello_world():
    return render_template('test.html')

@app.route("/add_data/<param>")
def add_gps_data(param):
#     import pdb; pdb.set_trace()
    lat, lon = param.split(',')
    gps_data_q.put((float(lat), float(lon)))
    return 'OK'


@app.route('/gps_data')
def stream():
    def eventStream():
        while True:
            lat, lon = gps_data_q.get()
            yield 'data: {}\n\n'.format(json.dumps({'lat': lat, 'lon': lon}))
    return Response(eventStream(), mimetype="text/event-stream")

app.run(host='0.0.0.0', port=3000, debug=True)