c = get_config()

c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = False
c.ServerApp.root_dir = '/workspace'
c.ServerApp.allow_origin = ''
c.ServerApp.allow_credentials = True
c.ServerApp.disable_check_xsrf = False
c.ServerApp.terminado_settings = {'shell_command': ['/bin/bash']}
