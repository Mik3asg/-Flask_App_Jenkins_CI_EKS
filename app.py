from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'We are deploying a Flask app into AWS EKS Cluster --- alpha.'