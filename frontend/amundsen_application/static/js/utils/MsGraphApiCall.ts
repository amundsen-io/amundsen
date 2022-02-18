import { loginRequest, graphConfig } from '../authConfig';
import { msalInstance } from '../index';

export async function callMsGraph() {
  const account = msalInstance.getActiveAccount();
  if (!account) {
    throw Error(
      'No active account! Verify a user has been signed in and setActiveAccount has been called.'
    );
  }

  const response = await msalInstance.acquireTokenSilent({
    ...loginRequest,
    account,
  });

  const headers = new Headers();
  const bearer = `Bearer ${response.accessToken}`;

  headers.append('Authorization', bearer);

  const options = {
    method: 'GET',
    headers,
  };

  return fetch(graphConfig.graphMeEndpoint, options)
    .then((response2) => {
      response2.json();
    })
    .catch((error) => console.log(error));
}
