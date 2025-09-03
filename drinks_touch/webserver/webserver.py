import json
import re
from datetime import datetime, timedelta
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import update

import config

from flask import Flask, make_response
from flask import render_template
from flask import request
from flask import send_file
from flask_compress import Compress

from database.models import Tx, Account
from database.storage import Base
from env import is_pi
from oidc import KeycloakAdmin
from stats.stats import scans
from users.qr import make_sepa_qr
from flask_oidc import OpenIDConnect


def create_oidc_config() -> dict:
    kc_admin = KeycloakAdmin()
    return {
        "web": {
            "client_id": kc_admin.client_id,
            "client_secret": kc_admin.client_secret,
            "auth_uri": kc_admin.authorization_endpoint,
            "token_uri": kc_admin.token_endpoint,
            "userinfo_uri": kc_admin.userinfo_endpoint,
            "issuer": kc_admin.issuer,
            "redirect_uris": [],
        }
    }


db = SQLAlchemy(
    model_class=Base,
    engine_options={
        "connect_args": {"application_name": "drinks_web"},
    },
)
app = Flask(__name__)
app.config.update(
    {
        "SQLALCHEMY_DATABASE_URI": config.POSTGRES_CONNECTION_STRING,
        "OIDC_CLIENT_SECRETS": create_oidc_config(),
        "SECRET_KEY": config.SECRET_KEY,
    }
)
db.init_app(app)
oidc = OpenIDConnect(app)
Compress(app)

uid_pattern = re.compile(r"^\d+$")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


@app.route("/favicon.png")
def favicon():
    return send_file("../resources/images/favicon.png", mimetype="image/png")


@app.route("/")
@app.route("/recharge")
def index():
    accounts = (
        db.session.query(Account).filter(Account.enabled).order_by(Account.name).all()
    )
    return render_template("index.html", accounts=accounts)


@app.route("/stats")
def stats():
    return render_template("stats.html")


@app.route("/recharge/doit", methods=["POST"])
def recharge_doit():
    user_id = request.form.get("user_user")
    if not user_id:
        return (
            render_template("message.html", message="Bitte einen Nutzer auswählen!"),
            400,
        )
    amount = request.form.get("amount")
    if not amount:
        return (
            render_template("message.html", message="Bitte einen Betrag angeben!"),
            400,
        )

    if amount == "0":
        return render_template("message.html", message="Ungültiger Betrag!"), 400

    account = db.session.query(Account).filter(Account.id == user_id).one()

    tx = Tx(
        payment_reference="Aufladung via Web",
        account_id=account.id,
        amount=Decimal(amount),
    )
    db.session.add(tx)
    db.session.commit()

    return render_template("recharge_success.html", amount=amount, account=account)


@app.route("/scans.json")
def scans_json():
    limit = int(request.args.get("limit", 1000))
    return to_json(scans(limit))


@app.route("/tx.png")
def tx_png():
    uid = request.args.get("uid")
    name = request.args.get("name")
    amount = request.args.get("amount")

    if not uid or not name or not amount:
        return "Please add parameters 'uid', 'name', and 'amount'!"

    if Decimal(amount) <= 0:
        return "Please use an amount greater than 0!"

    uid = int(uid)

    img_data = make_sepa_qr(amount, name, uid)
    response = make_response(img_data.getvalue())
    response.headers["Content-Type"] = "image/png"

    return response


@app.route("/enable_transaction_history/<signed_account_id>")
def enable_transaction_history(signed_account_id):
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
    return render_template(
        "enable_transaction_history_success.html", account_id=account_id
    )


def to_json(dict_arr):
    return json.dumps(dict_arr, cls=DateTimeEncoder)


def run():
    port = config.WEBSERVER_PORT

    app.run(host="0.0.0.0", debug=not is_pi(), port=port)
