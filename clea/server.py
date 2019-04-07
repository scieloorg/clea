from flask import Flask, flash, redirect, render_template, request, jsonify

from .core import Article
from .join import aff_contrib_full, aff_contrib_inner


app = Flask(__name__)
app.secret_key = "C(*JD@J(*HS@S)S("


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        try:
            xml_file = request.files["xml_file"]
        except KeyError:
            flash("Missing xml_file input")
            return redirect(request.url)
        try:
            article = Article(xml_file)
        except:
            flash("Error: can't load the given file")
            return redirect(request.url)
        return jsonify({**article.data_full,
            "aff_contrib_full": aff_contrib_full(article),
            "aff_contrib_inner": aff_contrib_inner(article),
        })
    return render_template("upload.html")
