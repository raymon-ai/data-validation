import os
import sys

import json
import time
import webbrowser
from multiprocessing import Process, Queue

import dash_html_components as html
from dwcl import DashWindowCloseListener
from flask import request

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

styles = {
    "pre": {"border": "thin lightgrey solid", "overflowX": "scroll"},
    "hidden": {"display": "none"},
}


def register_close(app, dash_input, dash_output):
    app.clientside_callback(
        """
        function(n_clicks) {
            if(n_clicks==1){
                window.close();
            }
            return 0;
        }
        """,
        dash_output,
        dash_input,
    )
    # Output('hidden-dummy', 'value'),
    # [Input('patch-setup-complete', 'n_clicks')],


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


def register_shutdown(app, fpath, dash_input, dash_output, dash_state):
    @app.callback(dash_output, dash_input, dash_state)
    def shutdown(n_clicks, state):
        if n_clicks == 0:
            raise PreventUpdate()
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        with open(fpath, "w") as f:
            json.dump(json.loads(state), f)
        print(f"State: \n{state}", flush=True)
        func()

        return "Setup complete."


def dash_app(func):
    def output_wrapped(*args, queue, **kwargs):
        returned = func(*args, **kwargs)
        queue.put(returned)

    def server_wrapped(*args, **kwargs):
        if "queue" in kwargs:
            raise ValueError(
                "The 'queue' kwarg is not allowed for functions wrapped with the 'dash_app' decorator as it is used internally. Please change the name of the parameter in the function."
            )
        else:
            queue = Queue()
            kwargs["queue"] = queue
        print(f"args: {args}, kwargs: {kwargs}")
        # Crease new process
        p = Process(target=output_wrapped, args=args, kwargs=kwargs)
        p.start()
        time.sleep(0.5)
        webbrowser.open_new("http://127.0.0.1:8050/")
        p.join()
        return queue.get()

    return server_wrapped
