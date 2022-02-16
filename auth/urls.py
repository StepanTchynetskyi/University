from flask import Blueprint

from auth import views

mod = Blueprint("auth", __name__, url_prefix="/auth")

mod.add_url_rule("/login", view_func=views.login_user, methods=["POST"])
mod.add_url_rule("/logout", view_func=views.logout_user, methods=["POST"])
mod.add_url_rule("/refresh", view_func=views.refresh, methods=["POST"])
