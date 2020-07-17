# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import os
from amundsen_application import create_app

application = create_app(
    config_module_class=os.getenv('FRONTEND_SVC_CONFIG_MODULE_CLASS') or
    'amundsen_application.config.LocalConfig')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
