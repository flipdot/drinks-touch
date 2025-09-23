import re
from datetime import timedelta
from decimal import Decimal

from itsdangerous import TimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import update

import config

from flask import Flask, make_response, session, g
from flask import render_template
from flask import request
from flask import send_file
from flask_compress import Compress

from database.models import Account
from env import is_pi
from oidc import KeycloakAdmin
from users.qr import make_sepa_qr

from .shared import db, oidc
from .blueprints.recharge import bp as recharge_bp
from .blueprints.account import bp as account_bp
from .blueprints.drinks import bp as drinks_bp


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
            "redirect_uris": [
                f"{config.BASE_URL}/authorize",
            ],
        }
    }


app = Flask(__name__)
app.config.update(
    {
        "SQLALCHEMY_DATABASE_URI": config.POSTGRES_CONNECTION_STRING,
        "OIDC_CLIENT_SECRETS": create_oidc_config(),
        "SECRET_KEY": config.SECRET_KEY,
        "SERVER_NAME": config.DOMAIN,
    }
)
db.init_app(app)
oidc.init_app(app)
Compress().init_app(app)

uid_pattern = re.compile(r"^\d+$")


app.register_blueprint(recharge_bp, url_prefix="/recharge")
app.register_blueprint(account_bp, url_prefix="/account")
app.register_blueprint(drinks_bp, url_prefix="/drinks")


@app.before_request
def load_current_user():
    if oidc.user_loggedin:
        if "account" not in g:
            subject = session["oidc_auth_profile"]["sub"]
            g.account = (
                db.session.query(Account).filter_by(keycloak_sub=subject).one_or_none()
            )
            if g.account is None:
                g.account = Account(
                    keycloak_sub=subject,
                    name=session["oidc_auth_profile"]["preferred_username"],
                    email=session["oidc_auth_profile"]["email"],
                )
                db.session.add(g.account)
                db.session.commit()
    else:
        g.account = None


@app.context_processor
def add_template_globals():
    if g.account:
        current_user = {
            "name": g.account.name,
            "sub": g.account.keycloak_sub,
            "balance": g.account.balance,
        }
    else:
        current_user = None

    navigation = [
        {"target": "index", "title": "Home"},
        {"target": "drinks.pricelist", "title": "Preisliste"},
        # {"target": "recharge", "title": "Tetris"},
    ]
    if current_user:
        navigation.extend(
            [
                {"target": "recharge.index", "title": "Guthaben aufladen"},
                # {"target": "account.index", "title": "Einstellungen"},
                # {"target": "recharge", "title": "Transaktionshistorie"},
            ]
        )
    return {
        "navigation": navigation,
        "current_user": current_user,
    }


# 404 handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def index():
    accounts = (
        db.session.query(Account).filter(Account.enabled).order_by(Account.name).all()
    )
    return render_template("index.html", accounts=accounts)


@app.route("/favicon.png")
def favicon():
    return send_file("../resources/images/favicon.png", mimetype="image/png")


@app.route("/tx.png")
def tx_png():
    uid = request.args.get("uid")
    name = request.args.get("name")
    amount = request.args.get("amount")

    if not uid or not name or not amount:
        return "Please add parameters 'uid', 'name', and 'amount'!"

    if Decimal(amount) <= 0:
        return "Please use an amount greater than 0!"

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


def run():
    port = config.WEBSERVER_PORT

    app.run(host="0.0.0.0", debug=not is_pi(), port=port)
