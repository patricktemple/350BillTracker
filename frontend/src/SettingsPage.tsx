import React, { useState } from 'react';
import useApiFetch from './useApiFetch';
import useMountEffect from '@restart/hooks/esm/useMountEffect';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import { User } from './types';
import InviteUserModal from './InviteUserModal';

export default function SettingsPage() {
  const [users, setUsers] = useState<User[] | null>(null);
  const apiFetch = useApiFetch();
  const [inviteUserModalVisible, setInviteUserModalVisible] = useState<boolean>(false);

  function loadUsers() {
    apiFetch('/api/users')
      .then((response) => response.json())
      .then((response) => {
        setUsers(response);
      });
  }
  useMountEffect(() => {
    loadUsers();
  });

  function handleInvite() {
    setInviteUserModalVisible(true);
  }

  function handleDelete(id: number) {
    apiFetch('/api/users/' + id, {
      method: 'DELETE',
    }
    ).then(response => response.json())
    .then(response => {
      loadUsers();
    });
  }

  function handleInviteUser(email: string, name: string) {
    apiFetch('/api/users/', {
      method: 'POST',
      body: JSON.stringify({ email, name }) // TODO: No json stringify, put that in apiFetch
    }
    ).then(response => response.json())
    .then(response => {
      loadUsers();
    });
    setInviteUserModalVisible(false);
  }


  return (<div>
    <h1>Settings</h1>
    <h2>Users</h2>
    <div>Invite 350 Brooklyn volunteers to access this bill tracker.</div>
    <Button onClick={handleInvite}>Invite</Button>
    <InviteUserModal show={inviteUserModalVisible} onHide={() => setInviteUserModalVisible(false)} handleInviteUser={handleInviteUser} />
    <Table striped bordered>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Delete?</th>
        </tr>
      </thead>
      <tbody>
        {users && users.map(user => <tr key={user.id}><td>{user.name}</td><td>{user.email}</td><td><Button variant="link" className="p-0" onClick={() => handleDelete(user.id)}>Delete</Button></td></tr>)}
      </tbody>
    </Table>
  </div>);
}