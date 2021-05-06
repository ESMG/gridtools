from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """serve the application with bokeh server"""
    Popen(["panel", "serve", "gridTools/mkMapInteractive.ipynb", "--allow-websocket-origin=*"])
