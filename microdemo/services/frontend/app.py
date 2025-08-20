from flask import Flask, render_template, request, redirect
import os, requests


app = Flask(__name__)
API_BASE = os.getenv("API_BASE", "http://api:8080")


@app.get("/healthz")
def healthz():
return {"status": "ok"}


@app.route("/", methods=["GET"])
def index():
try:
resp = requests.get(f"{API_BASE}/messages", timeout=2)
messages = resp.json()
except Exception:
messages = []
return render_template("index.html", messages=messages)


@app.post("/send")
def send():
author = request.form.get("author", "anon")
body = request.form.get("body", "")
if body:
try:
requests.post(f"{API_BASE}/messages", json={"author": author, "body": body}, timeout=2)
except Exception:
pass
return redirect("/")


if __name__ == "__main__":
app.run(host="0.0.0.0", port=8080)