from flask import Blueprint, render_template

from database.models import Drink
from webserver.shared import db

bp = Blueprint("drinks", __name__)


@bp.route("/pricelist")
def pricelist():
    query = db.select(Drink).order_by(Drink.name)
    drinks = db.paginate(query, per_page=20, max_per_page=100)
    return render_template("drinks/pricelist.html", drinks=drinks)
