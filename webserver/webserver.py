import datetime

from flask import Flask
from flask import request

from users.users import Users
from database.storage import get_session
from database.storage import init_db
from database.models.scan_event import ScanEvent

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

@app.route('/barcode_scanned')
def barcode_scanned():
    barcode = request.args.get('barcode')
    if barcode == None:
        return ('No Barcode send', 500)

    user = Users.get_active_user()
    if user == None:
        return ('No active user', 500)

    session = get_session()
    ev = ScanEvent(barcode, user['id'], datetime.datetime.now())
    
    session.add(ev)
    session.commit()

    from screens.screen_manager import ScreenManager
    screen = ScreenManager.get_instance().get_active()
    screen.back(None, None)  

    return 'ok'

def run(log):
    container['log'] = log
    app.run(
        host='0.0.0.0'
    )
