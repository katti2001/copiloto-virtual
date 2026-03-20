from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        return render_template("bienvenida.html", usuario=usuario)

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)