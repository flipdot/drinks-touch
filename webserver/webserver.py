from flask import Flask
from flask import request

app = Flask(__name__)

container = {}

@app.route('/')
def hello_world():
    msg = request.args.get('msg')

    if msg == None:
        return 'Please supply a "msg" request parameter'

    try:
        container['log'].log(msg)
        return 'ok'
    except Exception, e:
        print e

def run(log):
    container['log'] = log
    app.run(
        host='0.0.0.0'
    )
