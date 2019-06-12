import random

from flask import Flask, flash, redirect, render_template, request, jsonify

from .core import Article
from .join import aff_contrib_full_indices
from .misc import clean_empty


app = Flask(__name__)
app.secret_key = "%x" % random.getrandbits(128)


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
        return jsonify(clean_empty({
            **article.data_full,
            "filename": xml_file.filename,
            "aff_contrib_pairs": aff_contrib_full_indices(article),
        }))
    return render_template("upload.html")
