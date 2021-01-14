import os
import sys
from jupyter_dash import JupyterDash
import dash
import json
import time
import webbrowser
from multiprocessing import Process, Queue

import dash_html_components as html
from dwcl import DashWindowCloseListener
from flask import request

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def get_dash(mode="inline"):
    isnb = isnotebook()
    if isnb:
        print("Using JupyterDash")
        return JupyterDash, {"mode": mode}
    else:
        print("Using standard Dash")
        return dash.Dash, {}


def windowcloselistener(app, func=None):
    @app.callback(Output("page-listener-dummy", "children"), [Input("my-closed-listener", "status")])
    def detect_close(status):
        print(f"Close the browser window to stop this server.")
        if status is None or status == "mounted":
            return None
        shutdown = request.environ.get("werkzeug.server.shutdown")
        if shutdown is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        if func:
            print("Executing optionall callable")
            func()
        print(f"Stopping server...")
        shutdown()

    return html.Div(
        [
            DashWindowCloseListener(id="my-closed-listener"),
            html.Span(id="page-listener-dummy"),
        ]
    )


def dash_input(func):
    def output_wrapped(*args, queue, **kwargs):
        returned = func(*args, **kwargs)
        queue.put(returned)

    def server_wrapped(*args, **kwargs):
        if "queue" in kwargs:
            raise ValueError(
                "The 'queue' kwarg is not allowed for functions wrapped with the 'dash_input' decorator as it is used internally. Please change the name of the parameter in the function."
            )
        else:
            queue = Queue()
            kwargs["queue"] = queue
        # Crease new process
        p = Process(target=output_wrapped, args=args, kwargs=kwargs)
        p.start()
        time.sleep(0.5)
        webbrowser.open_new("http://127.0.0.1:8050/")
        p.join()
        return queue.get()

    return server_wrapped
