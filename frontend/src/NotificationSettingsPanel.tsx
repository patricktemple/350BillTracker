import React, { useState } from 'react';
import useApiFetch from './useApiFetch';
import useMountEffect from '@restart/hooks/useMountEffect';

export default function NotificationSettingsPanel() {
    const [notificationsEnabled, setNotificationsEnabled] = useState<boolean>(false);
    const apiFetch = useApiFetch();

    useMountEffect(() => {
        apiFetch('/api/users/viewer')
            .then(response => {
                setNotificationsEnabled(response.sendBillUpdateNotifications);
            });
    });

    function handleCheckboxChanged(e: any) {
        const enabled = e.target.checked;
        setNotificationsEnabled(enabled); // or checked?
        apiFetch('/api/users/viewer', {
            method: "PUT",
            body: {
                sendBillUpdateNotifications: enabled,
            }
        }).then(response => {
            // todo errors etc
            console.log('success');
        });
        // TODO: Call the API
    }
    return (
        <div>
            <h2>
                Notification Settings
            </h2>
            Enable noticications <input checked={notificationsEnabled} type="checkbox" onChange={handleCheckboxChanged} />
        </div>
    );
}