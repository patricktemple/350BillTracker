import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import './App.css';
import { CouncilMember } from './types';
import Accordion from 'react-bootstrap/Accordion';
import CouncilMemberDetails from './CouncilMemberDetails';
import { Form } from 'react-bootstrap';

interface Props {
  match: { params: { memberId?: number } };
}

export default function ConcilMembersPage({
  match: {
    params: { memberId }
  }
}: Props) {
  const [members, setMembers] = useState<CouncilMember[] | null>(null);
  const [filterText, setFilterText] = useState<string>('');

  useMountEffect(() => {
    fetch('/api/council-members')
      .then((response) => response.json())
      .then((response) => {
        setMembers(response);
      });
  });

  function handleFilterTextChanged(e: any) {
    setFilterText(e.target.value);
  }

  if (members) {
    const lowerFilterText = filterText.toLowerCase();
    const filteredMembers = members.filter(
      (m) =>
        m.name.toLowerCase().includes(lowerFilterText) ||
        m.borough?.toLowerCase().includes(lowerFilterText)
    );
    return (
      <div>
        <h2>Council members</h2>
        <input
          type="text"
          placeholder="Filter"
          value={filterText}
          className="mb-2"
          onChange={handleFilterTextChanged}
        />
        <Accordion defaultActiveKey={memberId?.toString()}>
          {filteredMembers.map((member) => (
            <Accordion.Item key={member.id} eventKey={member.id.toString()}>
              <Accordion.Header>
                <strong>{member.name}</strong>
                {member.borough && <>&nbsp;({member.borough})</>}
              </Accordion.Header>
              <Accordion.Body>
                <CouncilMemberDetails councilMember={member} />
              </Accordion.Body>
            </Accordion.Item>
          ))}
        </Accordion>
      </div>
    );
  }
  return <div>Loading...</div>;
}
