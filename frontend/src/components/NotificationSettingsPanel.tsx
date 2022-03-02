import React, { useState } from 'react';
import useApiFetch from '../useApiFetch';
import useMountEffect from '@restart/hooks/useMountEffect';
import styles from '../style/components/NotificationSettingsPanel.module.scss';
import Form from 'react-bootstrap/Form';
import { UserBillSettings, Uuid, Bill } from '../types';

interface BillSettings {
  [billId: Uuid]: UserBillSettings;
}

export default function NotificationSettingsPanel() {
  const [billSettings, setBillSettings] = useState<BillSettings | null>(null);
  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch('/api/viewer/bill-settings').then((response) => {
      const settingsMap: BillSettings = {};
      for (const setting of response) {
        settingsMap[setting.bill.id] = setting;
      }
      setBillSettings(settingsMap);
    });
  });

  function updateBillNotificationSettings(
    bill: Bill,
    sendBillUpdateNotifications: boolean
  ) {
    setBillSettings({
      ...billSettings,
      [bill.id]: {
        sendBillUpdateNotifications,
        bill
      }
    });
    apiFetch(`/api/bills/${bill.id}/viewer-settings`, {
      method: 'PUT',
      body: {
        sendBillUpdateNotifications
      }
    });
  }

  return (
    <div>
      <h2>Notification settings</h2>
      <p>
        Notify me by email whenever the status or sponsorships change on
        specific bills:
      </p>
      {billSettings == null
        ? 'Loading...'
        : Object.values(billSettings).map((s) => (
            <label key={s.bill.id} className={styles.bill}>
              <Form.Check
                className={styles.checkBox}
                id={s.bill.id}
                checked={s.sendBillUpdateNotifications}
                type={'checkbox'}
                onChange={(e: any) =>
                  updateBillNotificationSettings(s.bill, e.target.checked)
                }
              />
              {s.bill.displayName}{' '}
              <span className={styles.billCodeName}>({s.bill.codeName})</span>
            </label>
          ))}
    </div>
  );
}
