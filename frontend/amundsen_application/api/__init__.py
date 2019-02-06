import os
from typing import Any, IO, Tuple

from flask import Flask, render_template, send_from_directory
from flask import current_app as app


def init_routes(app: Flask) -> None:
    app.add_url_rule('/favicon.ico', 'favicon', favicon)
    app.add_url_rule('/healthcheck', 'healthcheck', healthcheck)
    app.add_url_rule('/', 'index', index, defaults={'path': ''})  # also functions as catch_all
    app.add_url_rule('/<path:path>', 'index', index)  # catch_all


def index(path: str) -> Any:
    return render_template("index.html")  # pragma: no cover


def healthcheck() -> Tuple[str, int]:
    return '', 200  # pragma: no cover


def favicon() -> IO[bytes]:
    """ TODO: Design team should provide us with a default icon """
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')  # pragma: no cover
