import React, { ReactElement, useState } from 'react';

const STORAGE_KEY = 'authToken';

// TODO: Handle token expiration
export interface AuthState {
  token: string | null;
  updateToken: (value: string | null) => void;
}

const defaultState = {
  token: null,
  updateToken: (value: string | null) => {
    console.log('null impl of updateToken');
  }
};

export const AuthContext = React.createContext<AuthState>(defaultState);

interface Props {
  children: ReactElement;
}

const initialValue = localStorage.getItem(STORAGE_KEY);

// TODO: This stuff needs tests now
export function AuthContextProvider(props: Props) {
  const [token, setToken] = useState<string | null>(initialValue);

  function updateToken(value: string | null) {
    if (value != null) {
      localStorage.setItem(STORAGE_KEY, value);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
    // TODO: This might not work in incognito? Session storage needed?
    setToken(token);
  }
  const value = { token, updateToken };

  return (
    <AuthContext.Provider value={value}>{props.children}</AuthContext.Provider>
  );
}
