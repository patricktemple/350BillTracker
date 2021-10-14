import React, { useState } from 'react';
import useApiFetch from './useApiFetch';
import useMountEffect from '@restart/hooks/useMountEffect';
import styles from './style/NotificationSettingsPanel.module.scss';
import Form from 'react-bootstrap/Form';

export default function NotificationSettingsPanel() {
  const [notificationsEnabled, setNotificationsEnabled] =
    useState<boolean>(false);
  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch('/api/viewer').then((response) => {
      setNotificationsEnabled(response.sendBillUpdateNotifications);
    });
  });

  function handleCheckboxChanged(e: any) {
    const enabled = e.target.checked;
    setNotificationsEnabled(enabled);
    apiFetch('/api/viewer', {
      method: 'PUT',
      body: {
        sendBillUpdateNotifications: enabled
      }
    });
  }
  return (
    <div>
      <h2 className={styles.title}>Alerts</h2>
      <Form.Check
        checked={notificationsEnabled}
        type={'checkbox'}
        label="Email me whenever a bill's status or sponsors change"
        onChange={handleCheckboxChanged}
      />
    </div>
  );
}
