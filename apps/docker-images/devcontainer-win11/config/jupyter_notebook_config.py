# DevContainer Win11 - Jupyter Notebook Configuration
# This is the default Jupyter config; runtime config is set by entrypoint.ps1

c = get_config()  # noqa

# Network settings
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False

# Working directory
c.ServerApp.root_dir = r'C:\workspace'

# Security (token/password set at runtime by entrypoint)
c.ServerApp.token = ''
c.ServerApp.password = ''
c.IdentityProvider.token = ''

# CORS
c.ServerApp.allow_origin = '*'
c.ServerApp.allow_credentials = True

# Disable root warning (we run as non-admin devuser, not root)
c.ServerApp.allow_root = False

# Kernel settings
c.KernelSpecManager.ensure_native_kernel = False

# Terminal
c.ServerApp.terminals_enabled = True

# Content manager
c.ContentsManager.allow_hidden = True
