from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from controller import processPolicyScatterPlot

app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/fetchPolicyScatterplot", methods=["GET"])
@cross_origin()
def fetchExample():
    points = processPolicyScatterPlot()
    resp = jsonify(data=points)
    return resp


if __name__ == "__main__":
    app.run(port=3100, debug=True)