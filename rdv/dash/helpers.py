from jupyter_dash import JupyterDash
import dash


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
