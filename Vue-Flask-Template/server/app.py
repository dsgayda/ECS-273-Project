from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from controller import processMap, processTopPoliciesPerState, processPolicyScatterplot, processGroupedBarChart, processPolicyCorrelations
import os
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/fetchMap", methods=["GET", "POST"])
@cross_origin()
def fetchMap():
    data = request.get_json()
    points = data.get("data", [])
    incident_type = data.get("incidentType", [])
    states = processMap(points, incident_type=incident_type)
    resp = jsonify(data=states)
    return resp


@app.route("/fetchPolicyScatterplot", methods=["GET", "POST"])
@cross_origin()
def fetchPolicyScatterplot():
    data = request.get_json()
    num_clusters = data.get("numClusters", [])
    reduction_type = data.get("reductionType", [])
    points, cluster_names = processPolicyScatterplot(num_clusters, reduction_type)
    resp = jsonify(data=points, clusters=cluster_names)
    return resp


@app.route("/fetchGroupedBarChart", methods=["GET", "POST"])
@cross_origin()
def fetchGroupedBarChart():
    data = request.get_json()
    points = data.get("data", [])
    cluster_names = data.get("clusters", [])

    bars = processGroupedBarChart(points, cluster_names)
    resp = jsonify(data=bars, clusters=cluster_names)
    return resp

@app.route("/fetchTopPoliciesPerPoint", methods=["GET", "POST"])
@cross_origin()
def fetchTopPoliciesPerPoint():
    top_policies = processTopPoliciesPerState()
    resp = jsonify(data=top_policies)
    return resp


@app.route("/fetchPolicyCorrelationTable", methods=["GET", "POST"])
@cross_origin()
def fetchPolicyCorrelationTable():
    data = request.get_json()
    points = data.get("data", [])
    incident_type = data.get("incidentType", [])
    table = processPolicyCorrelations(points, incidence_type=incident_type)
    resp = jsonify(data=table)
    return resp


@app.route("/fetchGeoMap", methods=["GET", "POST"])
@cross_origin()
def fetchGeoMap():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "data/map/states-albers-10m.json")
    with open(json_url) as json_file:
        data = json.load(json_file)
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=3100, debug=True)