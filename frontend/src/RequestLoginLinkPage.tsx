import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import React, { useState } from 'react';
import styles from './style/RequestLoginLinkPage.module.scss';

export default function RequestLoginLinkPage() {
  const [emailAddress, setEmailAddress] = useState<string>('');
  const [loginLinkSent, setLoginLinkSent] = useState<boolean>(false);
  const [requestInProgress, setRequestInProgress] = useState<boolean>(false);

  function emailAddressChanged(event: any) {
    setEmailAddress(event.target.value);
  }

  function handleSubmit(event: any) {
    event.preventDefault();
    setRequestInProgress(true);
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
        setRequestInProgress(false);
      });
  }

  return (
    <div className={styles.fullScreenContainer}>
    <div className={styles.pageContent}>
      <h1>Log in to 350 Brooklyn Bill Tracker</h1>
      <p>We&apos;ll email you a link you can click to login. No password needed.</p>
      <Form onSubmit={handleSubmit}>
          <Form.Control
            type="text"
            placeholder="Enter your email address"
            value={emailAddress}
            onChange={emailAddressChanged}
            size="sm"
          />

        <Button size="sm" type="submit" disabled={requestInProgress}>
          {requestInProgress ? "Requesting..." : "Request login link"}
        </Button>
        {loginLinkSent && <p className="mt-3">A link to login has been sent to this email address.</p>}
      </Form>
    </div>
    </div>
  );
}
