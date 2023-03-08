from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from controller import processMap, processPolicyScatterplot, processGroupedBarChart, processPolicyClusterCategories #, plotprocessExample

app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/fetchExample", methods=["GET", "POST"])
# @cross_origin()
# def fetchExample():
#     if request.method == "GET": # handling GET request
#         points, cluster_names = processExample()
#         resp = jsonify(data=points, clusters=cluster_names)
#         return resp
#     else: # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
#         request_context = request.get_json() # JSON object
#         method = request_context['method']
#         points, cluster_names = processExample(method)
#         resp = jsonify(data=points, clusters=cluster_names)
#         return resp

@app.route("/fetchMap", methods=["GET", "POST"])
@cross_origin()
def fetchMap():
    data = processMap()
    resp = jsonify(data=data)
    return resp


@app.route("/fetchPolicyScatterplot", methods=["GET", "POST"])
@cross_origin()
def fetchPolicyScatterplot():
    points, cluster_names = processPolicyScatterplot()
    resp = jsonify(data=points, clusters=cluster_names)
    return resp

@app.route("/fetchGroupedBarChart", methods=["GET", "POST"])
@cross_origin()
def fetchGroupedBarChart():
    points, cluster_names = processPolicyScatterplot()
    bars = processGroupedBarChart(points, cluster_names)
    resp = jsonify(data=bars, clusters=cluster_names)
    return resp

@app.route("/fetchPolicyClusterCategories", methods=["GET", "POST"])
@cross_origin()
def fetchPolicyClusterCategories():
    points, cluster_names = processPolicyScatterplot()
    categories = processPolicyClusterCategories(points, 2)
    resp = jsonify(data=categories)
    return resp



if __name__ == "__main__":
    app.run(port=3100, debug=True)