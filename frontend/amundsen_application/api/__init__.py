from typing import Any, Tuple

from flask import Flask, render_template


def init_routes(app: Flask) -> None:
    app.add_url_rule('/healthcheck', 'healthcheck', healthcheck)
    app.add_url_rule('/', 'index', index, defaults={'path': ''})  # also functions as catch_all
    app.add_url_rule('/<path:path>', 'index', index)  # catch_all


def index(path: str) -> Any:
    return render_template("index.html")  # pragma: no cover


def healthcheck() -> Tuple[str, int]:
    return '', 200  # pragma: no cover
