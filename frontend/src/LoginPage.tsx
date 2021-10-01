import React from 'react';
import Button from 'react-bootstrap/Button';

interface Props {
  login: () => void;
}

export default function LoginPage(props: Props) {
  return <Button onClick={props.login}>Login</Button>;
}