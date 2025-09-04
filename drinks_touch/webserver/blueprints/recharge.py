from decimal import Decimal

from flask import Blueprint, render_template, request, g, url_for

from webserver.shared import db, oidc

from database.models import Account, Tx

bp = Blueprint("recharge", __name__)


@bp.route("/")
@oidc.require_login
def index():
    # TODO: only recharge own account
    accounts = (
        db.session.query(Account).filter(Account.enabled).order_by(Account.name).all()
    )
    return render_template("recharge/index.html", accounts=accounts)


@bp.route("/", methods=["POST"])
@oidc.require_login
def submit():
    amount = request.form.get("amount")
    if not amount:
        return (
            render_template(
                "message.html",
                message="Bitte einen Betrag angeben!",
                auto_redirect_after=2,
            ),
            400,
        )

    if not request.form.get("confirm_cash_deposited"):
        return (
            render_template(
                "message.html",
                message="Bitte bestätige, dass du das Geld eingeworfen hast!",
                auto_redirect_after=2,
            ),
            400,
        )

    if amount == "0":
        return render_template("message.html", message="Ungültiger Betrag!"), 400

    tx = Tx(
        payment_reference="Aufladung via Web",
        account_id=g.account.id,
        amount=Decimal(amount),
    )
    db.session.add(tx)
    db.session.commit()

    return render_template(
        "recharge/success.html",
        amount=amount,
        account=g.account,
        auto_redirect_after=5,
        redirect_url=url_for("index"),
    )
