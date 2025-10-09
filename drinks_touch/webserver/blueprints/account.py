from flask import Blueprint, render_template, g, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField

from webserver.shared import oidc, db

bp = Blueprint("account", __name__)


class AccountForm(FlaskForm):
    tx_history_visible = BooleanField("Transaktionshistorie anzeigen")
    summary_email_notification_setting = SelectField(
        "Benachrichtigungen",
        choices=[
            ("instant", "Sofort"),
            ("daily", "Täglich"),
            ("instant and daily", "Sofort und Täglich"),
            ("weekly", "Wöchentlich"),
            ("instant and weekly", "Sofort und Wöchentlich"),
            ("never", "Nie"),
        ],
    )


@bp.route("/", methods=["GET", "POST"])
@oidc.require_login
def index():
    form = AccountForm(
        tx_history_visible=g.account.tx_history_visible,
        summary_email_notification_setting=g.account.summary_email_notification_setting,
    )
    if form.validate_on_submit():
        g.account.tx_history_visible = form.tx_history_visible.data
        g.account.summary_email_notification_setting = (
            form.summary_email_notification_setting.data
        )
        db.session.commit()
        flash("Einstellungen gespeichert", "success")
        return redirect(url_for("account.index"))
    return render_template("account/index.html", form=form)
