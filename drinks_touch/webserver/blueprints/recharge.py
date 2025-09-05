import decimal
from decimal import Decimal

from flask import Blueprint, render_template, g, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields.numeric import DecimalField
from wtforms.fields.simple import BooleanField
from wtforms.validators import InputRequired

from webserver.shared import db, oidc

from database.models import Tx

bp = Blueprint("recharge", __name__)


def validate_amount(form, field):
    field.data = field.data.quantize(Decimal("0.01"), rounding=decimal.ROUND_DOWN)
    if field.data == 0:
        raise validators.ValidationError("Darf nicht 0 sein.")


class RechargeForm(FlaskForm):
    amount = DecimalField(
        "Betrag",
        places=2,
        render_kw={
            "placeholder": "0.00",
            "step": "0.01",
        },
        validators=[InputRequired(message="Pflichtfeld"), validate_amount],
    )
    confirm_cash_deposited = BooleanField(
        "Ja, ich habe den Betrag in die Kasse eingeworfen",
        default=False,
        validators=[InputRequired(message="Pflichtfeld")],
    )


@bp.route("/", methods=["GET", "POST"])
@oidc.require_login
def index():
    form = RechargeForm()
    if form.validate_on_submit():
        amount = form.data["amount"]

        tx = Tx(
            payment_reference="Aufladung via Web",
            account_id=g.account.id,
            amount=amount,
        )
        db.session.add(tx)
        db.session.commit()

        flash(f"Guthaben wurde um {amount:.2f}€ aufgeladen.", "success")

        if amount < 0:
            flash(
                "Ein negativer Betrag… wusstest du, dass du auch Guthaben an andere übertragen kannst?",
                "info",
            )

        return redirect(url_for("index"))

    return render_template("recharge/index.html", form=form)
