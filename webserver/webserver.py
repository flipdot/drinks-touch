from flask import Flask

app = Flask(__name__)

container = {}

@app.route('/')
def hello_world():
    try:
        container['log'].log('this is a test')
        return 'ok'
    except Exception, e:
        print e

def run(log):
    container['log'] = log
    app.run()
