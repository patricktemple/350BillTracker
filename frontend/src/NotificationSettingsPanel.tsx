import React, { useState } from 'react';
import useApiFetch from './useApiFetch';
import useMountEffect from '@restart/hooks/useMountEffect';
import styles from './style/NotificationSettingsPanel.module.scss';
import Form from 'react-bootstrap/Form';
import { UserBillSettings, Uuid, Bill } from './types';

interface BillSettings {
  [billId: Uuid]: UserBillSettings;
}

export default function NotificationSettingsPanel() {
  const [billSettings, setBillSettings] =
    useState<BillSettings | null>(null);
  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch('/api/viewer/bill-settings').then((response) => {
      // hmm map is mutable... maybe best just to do this as a dict
      const settingsMap: BillSettings = {};
      for (const setting of response) {
        settingsMap[setting.bill.id] = setting;
      }
      setBillSettings(settingsMap);
    });
  });

  function updateBillNotificationSettings(bill: Bill, sendBillUpdateNotifications: boolean) {
    setBillSettings({
      ...billSettings,
      [bill.id]: {
        sendBillUpdateNotifications,
        bill,
      }
    });
    apiFetch(`/api/bills/${bill.id}/viewer-settings`, {
      method: 'PUT',
      body: {
        sendBillUpdateNotifications
      }
    });
  }

  // add Select All option?
  // make the name use "display name"
  // make "display name" a server-side thing

  return (
    <div>
      <h2 className={styles.title}>Notification settings</h2>
      <p>Notify me by email whenever the status or sponsorships change on specific bills:</p>
      {billSettings == null ? "Loading..." : Object.values(billSettings).map((s) => (
      <Form.Check
        key={s.bill.id}
        checked={s.sendBillUpdateNotifications}
        type={'checkbox'}
        label={s.bill.name}
        onChange={(e: any) => updateBillNotificationSettings(s.bill, e.target.checked)}
      />))}
    </div>
  );
}
