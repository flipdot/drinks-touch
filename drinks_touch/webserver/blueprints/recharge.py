from decimal import Decimal

from flask import Blueprint, render_template, g, url_for, flash
from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields.numeric import DecimalField
from wtforms.fields.simple import BooleanField

from webserver.shared import db, oidc

from database.models import Tx

bp = Blueprint("recharge", __name__)


class RechargeForm(FlaskForm):
    amount = DecimalField(
        "Betrag",
        places=2,
        render_kw={
            "placeholder": "0.00",
            "step": "0.01",
        },
        validators=[validators.Optional()],
    )
    confirm_cash_deposited = BooleanField(
        "Ja, ich habe den Betrag in die Kasse eingeworfen", default=False
    )


@bp.route("/", methods=["GET", "POST"])
@oidc.require_login
def index():
    form = RechargeForm(meta={"locales": ["de_DE", "de"]})
    if form.validate_on_submit():
        amount = form.data["amount"]
        form_invalid = False
        if not amount:
            flash("Bitte einen Betrag angeben!", "error")
            form_invalid = True

        if not form.data["confirm_cash_deposited"]:
            flash("Bitte bestätige, dass du das Geld eingeworfen hast!", "error")
            form_invalid = True

        if amount == "0":
            flash("Ungültiger Betrag!", "error")
            form_invalid = True

        if not form_invalid:
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
    return render_template("recharge/index.html", form=form)
