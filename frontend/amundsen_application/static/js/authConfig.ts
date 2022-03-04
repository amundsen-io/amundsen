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
  scopes: ['User.Read.All', 'GroupMember.Read.All'],
};

// Add here the endpoints for MS Graph API services you would like to use.
export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
  graphGroupsEndpoint: 'https://graph.microsoft.com/v1.0/me/memberOf',
};

export const securityGroups = {
  GroupMember: '8e8b6d2b-5aae-4228-810a-01e35dc4a2ae',
  GroupOwner: '079bbbc9-cc2c-4841-a535-b46b7ba4f7b6',
  GroupAdmin: '6ef14e7c-ca9a-43d7-90cc-a300c6b7f5fd',
};
