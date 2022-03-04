import React, { useState, useEffect } from 'react';
import { Route, Redirect } from 'react-router-dom';
import { useMsal } from '@azure/msal-react';
import { connect } from 'react-redux';

export const RouteGuard = ({ Component, ...props }) => {
  const { instance } = useMsal();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [currentAccount, setCurrentAccount] = useState({});

  const onLoad = async () => {
    const currentAccount = instance.getActiveAccount();

    setCurrentAccount(currentAccount || {});

    if (
      currentAccount &&
      currentAccount.idTokenClaims &&
      currentAccount.idTokenClaims.groups
    ) {
      const intersection = props.groups.filter((group) =>
        currentAccount.idTokenClaims
          ? currentAccount.idTokenClaims.groups.includes(group)
          : null
      );

      if (intersection.length > 0) {
        setIsAuthorized(true);
      }
    }
  };

  useEffect(() => {
    onLoad();
  }, [instance]);

  return (
    <>
      {isAuthorized ? (
        <Route
          {...props}
          render={(routeProps) => (
            <Component currentAccount={currentAccount} {...routeProps} />
          )}
        />
      ) : (
        <div style={{ textAlign: 'center' }}>
          <h3>You are unauthorized to view this content.</h3>
          <div>
            The user account{' '}
            <strong>{currentAccount ? currentAccount.username : ''}</strong> is
            not part of the Pharos group
          </div>
          <div>Contact the administrator if you need help accessing Pharos</div>
        </div>
      )}
    </>
  );
};
