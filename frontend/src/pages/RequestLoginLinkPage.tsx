import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import React, { useState } from 'react';
import styles from '../style/pages/RequestLoginLinkPage.module.scss';
import AppLogo from '../assets/app-logo.png';

// Need to render error message

interface Props {
  errorCode: string | null;
}

const ERROR_CODE_MESSAGES = new Map<string, string>([
  [
    'invalidLink',
    'The link you clicked was not valid. Please request a new one below.'
  ],
  [
    'alreadyUsed',
    'The link you clicked was already used. Please request a new one below.'
  ],
  [
    'linkExpired',
    'The link you clicked has expired. Please request a new one below.'
  ],
  ['unknownError', 'An unknown error occurred when logging you in.']
]);

export default function RequestLoginLinkPage(props: Props) {
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
        <img src={AppLogo} alt="Logo" className={styles.appLogo} />
        <h1>Log in to 350Brooklyn Bill Tracker</h1>
        {props.errorCode && (
          <div className={styles.errorMessage}>
            {ERROR_CODE_MESSAGES.get(props.errorCode)}
          </div>
        )}
        <p>
          We&apos;ll email you a link you can click to login. No password
          needed.
        </p>
        <Form onSubmit={handleSubmit}>
          <label
            htmlFor="RequestLoginLinkPage-email"
            className={styles.labelText}
          >
            Email Address
          </label>
          <Form.Control
            type="text"
            value={emailAddress}
            onChange={emailAddressChanged}
            size="sm"
            id="RequestLoginLinkPage-email"
          />

          <Button size="sm" type="submit" disabled={requestInProgress}>
            {requestInProgress ? 'Requesting...' : 'Request a link'}
          </Button>
          <div className={styles.statusText}>
            {statusText && <p>{statusText}</p>}
          </div>
        </Form>
      </div>
    </div>
  );
}
