import decimal
from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields.numeric import DecimalField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired

from database.models import Drink
from webserver.shared import db, oidc

bp = Blueprint("drinks", __name__)


def validate_price(form, field):
    if field.data is None:
        # Handled by default DecimalField validator ("Not a valid decimal value")
        return
    field.data = field.data.quantize(Decimal("0.01"), rounding=decimal.ROUND_DOWN)
    if field.data <= 0:
        raise validators.ValidationError("Preis muss positiv sein.")


class EditDrinkForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(message="Pflichtfeld")])
    price = DecimalField(
        "Preis",
        validators=[InputRequired(message="Pflichtfeld"), validate_price],
        places=2,
        render_kw={
            "placeholder": "0.00",
            "step": "0.01",
        },
    )


@bp.route("/pricelist")
def pricelist():
    query = db.select(Drink).order_by(Drink.name)
    drinks = db.paginate(query, per_page=20, max_per_page=100)
    return render_template("drinks/pricelist.html", drinks=drinks)


@bp.route("/<ean>/edit", methods=["GET", "POST"])
@oidc.require_login
def edit(ean):
    drink = db.one_or_404(db.select(Drink).filter_by(ean=ean))
    if not drink:
        return "Drink not found", 404

    form = EditDrinkForm(
        name=drink.name,
        price=drink.price,
    )
    if form.validate_on_submit():
        if request.form.get("action") == "delete":
            name = drink.name
            db.session.delete(drink)
            db.session.commit()
            flash(f"„{name}“ ({ean}) wurde gelöscht.", "success")
            return redirect(url_for("drinks.pricelist"))
        drink.name = form.name.data
        drink.price = form.price.data
        db.session.commit()
        flash(f"„{drink.name}“ wurde aktualisiert.", "success")
        return redirect(url_for("drinks.pricelist"))

    return render_template("drinks/edit.html", drink=drink, form=form)
