# Anthony Krivonos
# Oct 29, 2018
# src/servlet/server.py

# Global Imports
import sys
import os
import numpy as np
from os.path import join, dirname
from dotenv import load_dotenv
sys.path.append('src')

# Flask Imports
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth

# Local Imports
from query import *
from utility import *
import algorithms
from models import *

# Abstract: Starts a REST server to perform algorithm processes.

app = Flask(__name__)
auth = HTTPBasicAuth()

processes = {}

# /algorithm/run
# request name:String => Full name of algorithm to deploy.
# response Responds with a JSON status string.
# NOTE: Deploys the given algorithm on a new socket.
@app.route('/algorithm/run', methods=['POST'])
def algorithm_run():
    Utility.log(request.authorization["username"])
    Utility.log(request.authorization["password"])
    if not request.json or not 'name' in request.json or not request.authorization["username"] or not request.authorization["password"]:
        abort(400)
    query = None
    try:
        query = Query(request.authorization["username"], request.authorization["password"])
    except Exception as e:
        abort(401, "Could not log in: " + str(e))
    portfolio = query.user_portfolio()
    algorithm = getattr(algorithms, request.json['name'])(query, portfolio)
    process_id = str(Utility.now_timestamp())
    processes[process_id] = algorithm
    return jsonify({
        'algorithm_name': request.json['name'],
        'status': 'running',
        'process_id': process_id
    }), 200

# /algorithm/logs
# request process_id:String => String id of the algorithm process.
# response Responds with a JSON logs string.
# NOTE: Returns the entire list of logs for the given algorithm.
@app.route('/algorithm/logs', methods=['POST'])
def algorithm_logs():
    Utility.log(request.authorization["username"])
    Utility.log(request.authorization["password"])
    if not request.json or not 'process_id' in request.json or not request.authorization["username"] or not request.authorization["password"]:
        abort(400)
    elif request.json['process_id'] not in processes:
        abort(404)
    algorithm = processes[request.json['process_id']]
    algo_name = algorithm.name
    if algorithm.query.email != request.authorization["username"] or algorithm.query.password != request.authorization["password"]:
        abort(401)
    processes[request.json['process_id']] = None
    logs = algorithm.get_logs()
    return jsonify({
        'algorithm_name': algo_name,
        'status': 'running',
        'process_id': request.json['process_id'],
        'logs': logs
    }), 200

# /algorithm/stop
# request process_id:String => String id of the algorithm process.
# response Responds with a JSON status string.
# NOTE: Stops the algorithm and removes it from the processes map.
@app.route('/algorithm/stop', methods=['POST'])
def algorithm_stop():
    Utility.log(request.authorization["username"])
    Utility.log(request.authorization["password"])
    if not request.json or not 'process_id' in request.json or not request.authorization["username"] or not request.authorization["password"]:
        abort(400)
    elif request.json['process_id'] not in processes:
        abort(404)
    algorithm = processes[request.json['process_id']]
    algo_name = algorithm.name
    if algorithm.query.email != request.authorization["username"] or algorithm.query.password != request.authorization["password"]:
        abort(401)
    processes[request.json['process_id']] = None
    return jsonify({
        'algorithm_name': algo_name,
        'status': 'stopped',
        'process_id': request.json['process_id']
    }), 200


if __name__ == '__main__':
     app.run()