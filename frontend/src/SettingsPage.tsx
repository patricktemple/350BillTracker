import React, { useState } from 'react';
import useApiFetch from './useApiFetch';
import useMountEffect from '@restart/hooks/esm/useMountEffect';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import { User, Uuid } from './types';
import InviteUserModal from './InviteUserModal';
import style from './style/SettingsPage.module.scss';
import UserList from './UserList';

export default function SettingsPage() {
  const [users, setUsers] = useState<User[] | null>(null);
  const apiFetch = useApiFetch();
  const [inviteUserModalVisible, setInviteUserModalVisible] =
    useState<boolean>(false);

  function loadUsers() {
    apiFetch('/api/users').then((response) => {
      setUsers(response);
    });
  }
  useMountEffect(() => {
    loadUsers();
  });

  function handleInvite() {
    setInviteUserModalVisible(true);
  }

  function handleDelete(id: Uuid) {
    apiFetch('/api/users/' + id, {
      method: 'DELETE'
    }).then((response) => {
      loadUsers();
    });
  }

  function handleInviteUser(email: string, name: string) {
    apiFetch('/api/users', {
      method: 'POST',
      body: { email, name }
    })
      .then((response) => response.json())
      .then((response) => {
        loadUsers();
      });
    setInviteUserModalVisible(false);
  }

  return (
    <div>
      <h1 className={style.title}>Settings</h1>
      <div className={style.content}>
        <h2>Users</h2>
        <p>
          Invite 350 Brooklyn volunteers to access this bill tracker.
          They&apos;ll need to be on this list in order to log in.
        </p>
        <div style={{ textAlign: 'right' }}>
          <Button onClick={handleInvite} size="sm" className="mb-2">
            Invite
          </Button>
        </div>
        <InviteUserModal
          show={inviteUserModalVisible}
          onHide={() => setInviteUserModalVisible(false)}
          handleInviteUser={handleInviteUser}
        />

        {users == null ? (
          'Loading...'
        ) : (
          <UserList handleDelete={handleDelete} users={users} />
        )}
      </div>
    </div>
  );
}
