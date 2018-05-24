from flask import Flask, abort, render_template, request, jsonify

from core import Article


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        try:
            xml_file = request.files["xml_file"]
            article = Article(xml_file)
        except:
            abort(400)
        return jsonify(article.data)
    return render_template("upload.html")
