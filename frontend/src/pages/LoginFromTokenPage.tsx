import React, { useContext } from 'react';
import { AuthContext, AuthState } from '../AuthContext';
import { Redirect } from 'react-router-dom';
import useMountEffect from '@restart/hooks/useMountEffect';

async function login(token: string, authState: AuthState) {
  const response = await fetch(`/api/login`, {
    method: 'POST',
    body: JSON.stringify({ token }),
    headers: {
      'Content-Type': 'application/json'
    }
  });
  const responseJson = await response.json();
  if (response.status === 401) {
    window.location.replace('/#' + responseJson['errorCode']);
  } else {
    authState?.updateToken(responseJson['authToken']);
    window.location.replace('/');
  }
}

// This is not a login screen. Instead it just looks for a token in the
// URL params, calls the login API, and then updates the state.
export default function LoginFromTokenPage() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);

  const token = urlParams.get('token');
  const authContext = useContext(AuthContext);

  useMountEffect(() => {
    if (!token) {
      window.location.replace('/#invalidToken');
    } else if (authContext) {
      login(token, authContext);
    }
  });

  return <div>Logging in...</div>;
}
