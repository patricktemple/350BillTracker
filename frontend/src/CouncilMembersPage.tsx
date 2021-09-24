import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import './App.css';
import { CouncilMember } from './types';

interface Props {
  members: CouncilMember[] | null;
}

export default function CouncilMembersPage() {
  const [members, setMembers] = useState<any>(null);

  useMountEffect(() => {
    fetch('/api/council-members')
      .then((response) => response.json())
      .then((response) => {
        setMembers(response);
      });
  });

  if (members) {
    return (
      <Table striped bordered>
        <thead>
          <tr>
            <th>Name</th>
            <th>Term Start</th>
            <th>Term End</th>
            <th>Email</th>
            <th>District Phone</th>
            <th>Legislative Phone</th>
          </tr>
        </thead>
        <tbody>
          {members.map((member: any) => (
            <tr key={member.id}>
              <td>{member.name}</td>
              <td>{member.termStart}</td>
              <td>{member.termEnd}</td>
              <td>{member.email}</td>
              <td>{member.districtPhone}</td>
              <td>{member.legislativePhone}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    );
  }
  return <div>Loading...</div>;
}
