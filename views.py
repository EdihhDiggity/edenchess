from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from get_games import get_games_from_archives

views = Blueprint(__name__, "views")

@views.route("/", methods=["POST", "GET"])
def importGame():
    if request.method == "POST":
        username = request.form["username"]
        return redirect(url_for("views.analysis", usrnm = username))
    else:
        return render_template("importGame.html")

@views.route("/analysis/<usrnm>")
def analysis(usrnm):
    return render_template("gameInsights.html", username = usrnm)

@views.route("/api/analysis/<usrnm>")
def api_analysis(usrnm):
    game_data = get_games_from_archives(usrnm)
    return jsonify(game_data)
