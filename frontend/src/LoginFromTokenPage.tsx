import React, { useContext } from 'react';
import { AuthContext } from './AuthContext';
import { Redirect } from 'react-router-dom';

// This is not a login screen. Instead it just looks for a token in the
// URL params, calls the login API, and then updates the state.
export default function LoginFromTokenPage() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);

  const token = urlParams.get("token");
  const authContext = useContext(AuthContext);

  fetch(`/api/login`, {
    method: 'POST',
    body: JSON.stringify({ token }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then((response) => response.json())
    .then((response) => {
      authContext?.updateToken(response['authToken']);
    });
  
  return <div>Logging in...</div>;
}