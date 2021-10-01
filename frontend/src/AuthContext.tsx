import React, { ReactElement, useState } from 'react';

export interface AuthState {
  token: string | null;
  updateToken: (value: string) => void;
}

const defaultState = {
  token: null,
  updateToken: (value: string) => {
    console.log("null impl of updateToken")
  },
}

export const AuthContext = React.createContext<AuthState>(defaultState);

interface Props {
  children: ReactElement;
}

export function AuthContextProvider(props: Props) {
  const [token, setToken] = useState<string | null>(null);

  // TODO: Use localStorage
  function updateToken(value: string) {
    setToken(token);
    window.alert("Updating token to " + value);
  }
  const value = { token: "hi", updateToken };

  return <AuthContext.Provider value={value}>{props.children}</AuthContext.Provider>;
}