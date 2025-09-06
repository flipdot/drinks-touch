from flask import Blueprint, render_template

from webserver.shared import oidc

bp = Blueprint("account", __name__)


@bp.route("/")
@oidc.require_login
def index():
    return render_template("account/index.html")
