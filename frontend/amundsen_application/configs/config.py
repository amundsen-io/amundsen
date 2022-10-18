from amundsen_application.config import LocalConfig
from amundsen_application.oidc_config import OidcConfig

import os
from os import environ

class FrontendConfigAuth(OidcConfig):
    if 'ISSUE_TRACKER_URL' in os.environ:
        ISSUE_LABELS = []  # type: List[str] (Optional labels to be set on the created tickets)
        ISSUE_TRACKER_URL = os.environ['ISSUE_TRACKER_URL']  # type: str (Your JIRA environment, IE 'https://jira.net')
        ISSUE_TRACKER_USER = os.environ['ISSUE_TRACKER_USER']  # type: str (Recommended to be a service account)
        ISSUE_TRACKER_PASSWORD = os.environ['ISSUE_TRACKER_PASSWORD']  # type: str
        ISSUE_TRACKER_PROJECT_ID = os.environ['ISSUE_TRACKER_PROJECT_ID']  # type: int (Project ID for the project you would like JIRA tickets to be created in)
        ISSUE_TRACKER_CLIENT = 'amundsen_application.client.jira.cloud_jira_client.CloudJiraClient'  # type: str (Fully qualified class name and path)
        ISSUE_TRACKER_CLIENT_ENABLED = True  # type: bool (Enabling the feature, must be set to True)
        ISSUE_TRACKER_MAX_RESULTS = 5  # type: int (Max issues to display at a time)
        ISSUE_TRACKER_ISSUE_TYPE_ID = 10002 # type: int (Jira only: Override default issue tracker ID whenever needed for cloud/hosted deployments)

    SQLALCHEMY_DATABASE_URI='sqlite:///sessions.db'

    SESSION_TYPE='sqlalchemy'

    FLASK_OIDC_SECRET_KEY='base-flask-oidc-secret-key'

    FLASK_OIDC_LOG_DATE_FORMAT='%Y-%m-%dT%H:%M:%S%z'

    pass

class FrontendConfig(LocalConfig):
    if 'ISSUE_TRACKER_URL' in os.environ:
        ISSUE_LABELS = []  # type: List[str] (Optional labels to be set on the created tickets)
        ISSUE_TRACKER_URL = os.environ['ISSUE_TRACKER_URL']  # type: str (Your JIRA environment, IE 'https://jira.net')
        ISSUE_TRACKER_USER = os.environ['ISSUE_TRACKER_USER']  # type: str (Recommended to be a service account)
        ISSUE_TRACKER_PASSWORD = os.environ['ISSUE_TRACKER_PASSWORD']  # type: str
        ISSUE_TRACKER_PROJECT_ID = os.environ['ISSUE_TRACKER_PROJECT_ID']  # type: int (Project ID for the project you would like JIRA tickets to be created in)
        ISSUE_TRACKER_CLIENT = 'amundsen_application.client.jira.cloud_jira_client.CloudJiraClient'  # type: str (Fully qualified class name and path)
        ISSUE_TRACKER_CLIENT_ENABLED = True  # type: bool (Enabling the feature, must be set to True)
        ISSUE_TRACKER_MAX_RESULTS = 5  # type: int (Max issues to display at a time)
        ISSUE_TRACKER_ISSUE_TYPE_ID = 10002 # type: int (Jira only: Override default issue tracker ID whenever needed for cloud/hosted deployments)

    SQLALCHEMY_DATABASE_URI='sqlite:///sessions.db'

    SESSION_TYPE='sqlalchemy'

    pass