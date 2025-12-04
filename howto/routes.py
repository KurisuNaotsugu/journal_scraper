from flask import Blueprint, render_template

from . import howto_bp

@howto_bp.route("/howto", methods=["GET"])
def howto():
    return render_template("howto.html")
