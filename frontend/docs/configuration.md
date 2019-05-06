# Configuration

## Flask
The default Flask application uses a [LocalConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) that looks for the metadata and search services running on localhost. In order to use different end point, you need to create a custom config class suitable for your use case. Once the config class has been created, it can be referenced via the [environment variable](https://github.com/lyft/amundsenfrontendlibrary/blob/4bf244d85bf82319b14919358691fd47a094e821/amundsen_application/wsgi.py#L5): `FRONTEND_SVC_CONFIG_MODULE_CLASS`

For more information on how the configuration is being loaded and used, please reference the official Flask [documentation](http://flask.pocoo.org/docs/1.0/config/#development-production).

## React Application

### Application Config
Certain features of the React application import variables from an [AppConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config.ts#L5) object. The configuration can be customized by modifying [config-custom.ts](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config-custom.ts).

#### Example: Add a custom logo

1. Add your logo to the folder in `amundsen_application/static/images/`
2. Set the the `logoPath` key on the `AppConfigCustom` object in [config-custom.ts](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config-custom.ts). For example Lyft uses the value `"/static/images/lyft-logo.svg"`
3. Rebuild/redeploy. 
   * `npm run build` to rebuild typescript files to reference the new logo image
   * `python3 setup.py install` will updated deployed files and make the new image available on the server

### Custom Fonts & Styles
Fonts and css variables can be customized by modifying [fonts-custom.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_fonts-custom.scss) and
[variables-custom.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_variables-custom.scss).
