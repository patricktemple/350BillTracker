import { useContext } from 'react';
import { AuthContext } from './AuthContext';

interface ApiFetchParams {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
}

export default function useApiFetch() {
  const authContext = useContext(AuthContext);

  const headers: any = {
    'Content-Type': 'application/json'
  };

  if (authContext.token != null) {
    headers['Authorization'] = 'JWT ' + authContext.token;
  }

  async function apiFetch(path: string, params?: ApiFetchParams) {
    const fetchParams = params || {};
    if (fetchParams.body != null) {
      fetchParams.body = JSON.stringify(fetchParams.body);
    }
    const response = await fetch(path, {
      headers,
      ...fetchParams
    });
    if (response.ok) {
      return response.json();
    }

    if (response.status === 401) {
      // Assume that the token has expired. Refresh to be bounced to the login page.
      authContext.updateToken(null);
      window.location.reload();
    }
  
    throw Error("API call failed with status " + response.status);
  }

  return apiFetch;
}
