import { useContext } from 'react';
import { AuthContext } from './AuthContext';

interface ApiFetchParams {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any; // or Record of some type?
}

export default function useApiFetch() {
  const authContext = useContext(AuthContext);

  const headers: any = {
    'Content-Type': 'application/json'
  };

  if (authContext.token != null) {
    headers['Authorization'] = 'JWT ' + authContext.token;
  }

  // TODO: Handle JSON.stringify for callers, too
  function apiFetch(path: string, params?: ApiFetchParams) {
    const fetchParams = params || {};
    return fetch(path, {
      headers,
      ...fetchParams
    });
  }

  return apiFetch;
}
