import datetime

from flask import Flask
from flask import request
from flask import render_template

from users.users import Users
from database.storage import get_session
from database.storage import init_db
from database.models.recharge_event import RechargeEvent


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recharge')
def recharge():
    users = Users.get_all()
    users.insert(0,{})
    return render_template('recharge.html', users=users)

@app.route('/recharge/doit', methods=['POST'])
def recharge_doit():
    user = request.form['user_user']
    helper = request.form['helper_user']
    amount = request.form['amount']

    if not user or not helper or amount <= 0:
        return 'Please enter valid data!'

    session = get_session()
    ev = RechargeEvent(
        user,
        helper,
        amount
    )
    
    session.add(ev)
    session.commit()

    return render_template('recharge_success.html', amount=amount)


def run():
    app.run(
        host='0.0.0.0'
    )
