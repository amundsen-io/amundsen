import { Configuration, PopupRequest } from '@azure/msal-browser';

// Config object to be passed to Msal on creation
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.REACT_APP_CLIENT_ID || 'none',
    authority:
      'https://login.microsoftonline.com/19bc8e68-8368-4080-bebb-16dac70496ef',
    redirectUri: process.env.REACT_APP_REDIRECT_URI,
  },
};

// Add here scopes for id token to be used at MS Identity Platform endpoints.
export const loginRequest: PopupRequest = {
  scopes: ['User.Read.All'],
};

// Add here the endpoints for MS Graph API services you would like to use.
export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
};
