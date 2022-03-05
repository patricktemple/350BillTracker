import React, { useContext } from 'react';
import { AuthContext } from '../AuthContext';
import { Redirect } from 'react-router-dom';
import useMountEffect from '@restart/hooks/useMountEffect';

// This is not a login screen. Instead it just looks for a token in the
// URL params, calls the login API, and then updates the state.
export default function LoginFromTokenPage() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);

  const token = urlParams.get('token');
  const authContext = useContext(AuthContext);

  useMountEffect(() => {
    fetch(`/api/login`, {
      method: 'POST',
      body: JSON.stringify({ token }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((response) => {
        // if (response.status === 401) {
        //   const errorMessage = response['errorCode'];
        //   window.location.replace('/#' + response['errorCode']); // TODO
        // }
        authContext?.updateToken(response['authToken']);
        window.location.replace('/');
        // TODO: Handle the possible error messages
      });
  });

  return <div>Logging in...</div>;
}
