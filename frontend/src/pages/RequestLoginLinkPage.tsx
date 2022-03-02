import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import React, { useState } from 'react';
import styles from '../style/pages/RequestLoginLinkPage.module.scss';
import AppLogo from '../assets/app-logo.png';

export default function RequestLoginLinkPage() {
  const [emailAddress, setEmailAddress] = useState<string>('');
  const [statusText, setStatusText] = useState<string | null>(null);
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
      .then((response) => {
        if (response.status == 422) {
          throw Error(
            'You must be invited to this tool before you can use it. Ask for an invite from a 350Brooklyn administrator.'
          );
        }
        if (!response.ok) {
          throw Error('An unexpected error occurred.');
        }
        return response.json();
      })
      .then((response) => {
        setStatusText('A link to login has been sent to this email address.');
        setRequestInProgress(false);
      })
      .catch((err) => {
        setStatusText(err.message);
        setRequestInProgress(false);
      });
  }

  return (
    <div className={styles.fullScreenContainer}>
      <div className={styles.pageContent}>
        <img src={AppLogo} alt="Logo" className={styles.appLogo}/>
        <h1>Log in to 350Brooklyn Bill Tracker</h1>
        <p>
          We&apos;ll email you a link you can click to login. No password
          needed.
        </p>
        <Form onSubmit={handleSubmit}>
          <label>
            <span className={styles.labelText}>Email Address</span>
          <Form.Control
            type="text"
            placeholder="Enter your email address"
            value={emailAddress}
            onChange={emailAddressChanged}
            size="sm"
          />
          </label>

          <Button size="sm" type="submit" disabled={requestInProgress}>
            {requestInProgress ? 'Requesting...' : 'Request a link'}
          </Button>
          {statusText && <p className="mt-3">{statusText}</p>}
        </Form>
      </div>
    </div>
  );
}
