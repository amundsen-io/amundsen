import os
from amundsen_application import create_app

app = create_app(
    config_module_class=os.getenv('FRONTEND_SVC_CONFIG_MODULE_CLASS') or
    'amundsen_application.config.LocalConfig')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
