import json
import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import update

import config

from flask import Flask, make_response
from flask import render_template
from flask import request
from flask_compress import Compress

from database.models import Tx, Account
from database.storage import Base
from env import is_pi
from stats.stats import scans
from users.qr import make_sepa_qr


db = SQLAlchemy(
    model_class=Base,
    engine_options={
        "connect_args": {"application_name": "drinks_web"},
    },
)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.POSTGRES_CONNECTION_STRING
db.init_app(app)
Compress(app)

uid_pattern = re.compile(r"^\d+$")


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@app.route("/accounts")
def accounts_get():
    return (
        db.session.query(Account).filter(Account.enabled).order_by(Account.name).all()
    )


@app.route("/transaction", methods=["POST"])
def transaction_post():
    user_id = request.form.get("user_user")
    if not user_id:
        return (
            "DTUNF",  # user not found
            400,  # message.html: Bitte einen Nutzer auswählen!
        )
    amount = request.form.get("amount")
    if not amount:
        return (
            "DTANF",  # amount not found
            400,  # message.html: Bitte einen Betrag angeben!
        )

    if amount == "0":
        return (
            "DTAIV",  # amount invalid
            400,  # message.html: Ungültiger Betrag!
        )

    account = db.session.query(Account).filter(Account.id == user_id).one()

    tx = Tx(
        payment_reference="Aufladung via Web",
        account_id=account.id,
        amount=Decimal(amount),
    )
    db.session.add(tx)
    db.session.commit()

    # recharge_success.html
    response = make_response(
        to_json(
            {
                amount,
                account,
            }
        )
    )
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/transactions")
def transactions_get():
    limit = int(request.args.get("limit", 1000))
    response = make_response(to_json(scans(limit)))
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/sepa/qr-code")
def sepa_qr_code_get():
    uid = request.args.get("uid")
    name = request.args.get("name")
    amount = request.args.get("amount")

    if not uid or not name or not amount:
        return (
            "DTPNF",  # property not found
            400,  # Please add parameters 'uid', 'name', and 'amount'!
        )

    if Decimal(amount) <= 0:
        return (
            "DTATS",  # amount too small
            400,  # Please use an amount greater than 0!
        )

    uid = int(uid)

    img_data = make_sepa_qr(amount, name, uid)
    response = make_response(img_data.getvalue())
    response.headers["Content-Type"] = "image/png"

    return response


@app.route("/transactions/history/enable", methods=["POST"])
def enable_transaction_history():
    content = request.json
    signed_account_id = content.signed_account_id
    signer = TimedSerializer(config.SECRET_KEY, salt="enable_transaction_history")

    try:
        account_id = signer.loads(
            signed_account_id, max_age=timedelta(days=1).total_seconds()
        )
    except SignatureExpired:
        return render_template("message.html", message="Link abgelaufen"), 400
    except BadSignature:
        return render_template("message.html", message="Ungültiger Link"), 400

    query = (
        update(Account).where(Account.id == account_id).values(tx_history_visible=True)
    )
    db.session.execute(query)
    db.session.commit()

    return account_id  # enable_transaction_history_success.html


def to_json(dict_arr):
    return json.dumps(dict_arr, cls=Encoder)


def run():
    port = config.WEBSERVER_PORT

    app.run(host="0.0.0.0", debug=not is_pi(), port=port)
