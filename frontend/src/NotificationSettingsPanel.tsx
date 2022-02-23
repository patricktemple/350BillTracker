import React, { useState } from 'react';
import useApiFetch from './useApiFetch';
import useMountEffect from '@restart/hooks/useMountEffect';
import styles from './style/NotificationSettingsPanel.module.scss';
import Form from 'react-bootstrap/Form';
import { UserBillSettings } from './types';

export default function NotificationSettingsPanel() {
  const [billSettings, setBillSettings] =
    useState<UserBillSettings[] | null>(null);
  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch('/api/viewer/bill-settings').then((response) => {
      setBillSettings(response);
    });
  });

  // function handleCheckboxChanged(e: any) {
  //   const enabled = e.target.checked;
  //   setNotificationsEnabled(enabled);
  //   apiFetch('/api/viewer', {
  //     method: 'PUT',
  //     body: {
  //       sendBillUpdateNotifications: enabled
  //     }
  //   });
  // }

  // add Select All option?
  // make the name use "display name"
  // make "display name" a server-side thing

  return (
    <div>
      <h2 className={styles.title}>Notification settings</h2>
      <p>Notify me by email whenever the status or sponsorships change on specific bills:</p>
      {billSettings == null ? "Loading..." : billSettings.map((s) => (
      <Form.Check
        key={s.bill.id}
        checked={s.sendBillUpdateNotifications}
        type={'checkbox'}
        label={s.bill.name}
        // onChange={handleCheckboxChanged}
      />))}
    </div>
  );
}
