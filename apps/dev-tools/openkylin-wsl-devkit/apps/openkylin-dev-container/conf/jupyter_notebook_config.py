# jupyter_notebook_config.py — JupyterLab for the openKylin dev container.
# Runs as devuser on 0.0.0.0:8888, root_dir /workspace.
# SECURITY NOTE: token/password are disabled for local-development convenience;
# never expose port 8888 to the public internet.

c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.token = ""
c.ServerApp.password = ""
c.ServerApp.root_dir = "/workspace"
c.ServerApp.allow_hidden = True
c.ServerApp.terminals_enabled = True

c.ServerApp.iopub_data_rate_limit = 10000000
