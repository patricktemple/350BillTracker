import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import React, { useState } from 'react';


export default function RequestLoginLinkPage() {
  const [emailAddress, setEmailAddress] = useState<string>("");
  const [loginLinkSent, setLoginLinkSent] = useState<boolean>(false);

  function emailAddressChanged(event: any) {
    setEmailAddress(event.target.value);
  }

  function handleSubmit(event: any) {
    event.preventDefault();
    fetch(`/api/create-login-link`, {
      method: 'POST',
      body: JSON.stringify({ email: emailAddress }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    // TODO: Handle failed login
      .then((response) => response.json())
      .then((response) => {
        setLoginLinkSent(true);
      });
  }

  return (
    <Form onSubmit={handleSubmit}>
    <Form.Group className="mb-3">
      <Form.Label>
        Email address:
      </Form.Label>
      <Form.Control
        type="text"
        placeholder="Enter your email address"
        value={emailAddress}
        onChange={emailAddressChanged}
      />
    </Form.Group>

    <Button variant="primary" type="submit" className="mb-2">
      Request login link
    </Button>
    {loginLinkSent && "A link to login has been sent to this email address."}
  </Form>
    );
}