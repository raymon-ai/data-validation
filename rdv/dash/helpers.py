from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import request
import json

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
