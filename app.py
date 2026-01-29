from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "repuestos.json"

# --- Config ---
SERVICE_PASSWORD = os.getenv("WS_PASSWORD", "wiener123")  # cambiable por variable de entorno
SECRET_KEY = os.getenv("WS_SECRET_KEY", "change-me-please")  # para sesiones

app = Flask(__name__)
app.secret_key = SECRET_KEY


def load_parts() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def norm(s: str) -> str:
    return "".join(str(s).strip().upper().split())


def find_part(code: str, parts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    q = norm(code)
    if not q:
        return None

    # índice simple
    for p in parts:
        if norm(p.get("codigo_wiener", "")) == q:
            return p
        if norm(p.get("codigo_original", "")) == q:
            return p
    return None


def require_login():
    return session.get("logged_in") is True


@app.get("/")
def home():
    if require_login():
        return redirect(url_for("search"))
    return redirect(url_for("login"))


@app.get("/login")
def login():
    return render_template("login.html")


@app.post("/login")
def login_post():
    pwd = request.form.get("password", "")
    if pwd == SERVICE_PASSWORD:
        session["logged_in"] = True
        return redirect(url_for("search"))
    flash("Contraseña incorrecta.", "error")
    return redirect(url_for("login"))


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/search")
def search():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("search.html", part=None, q="")


@app.post("/search")
def search_post():
    if not require_login():
        return redirect(url_for("login"))

    q = request.form.get("query", "")
    parts = load_parts()
    part = find_part(q, parts)

    if not q.strip():
        flash("Ingresá un código para buscar.", "error")
        return render_template("search.html", part=None, q=q)

    if part is None:
        flash("No se encontró ese código (Wiener u Original).", "error")
        return render_template("search.html", part=None, q=q)

    flash("Repuesto encontrado ✅", "ok")
    return render_template("search.html", part=part, q=q)


if __name__ == "__main__":
    # http://127.0.0.1:5000
    app.run(debug=True)