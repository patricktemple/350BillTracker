import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import { Person, CouncilMember } from './types';
import Accordion from 'react-bootstrap/Accordion';
import PersonDetailsPanel from './PersonDetailsPanel';
import { Form } from 'react-bootstrap';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';
import styles from './style/LegislatorsPage.module.scss';

interface Props {
  match: { params: { personId?: string } };
}

export default function ConcilMembersPage({
  match: {
    params: { personId }
  }
}: Props) {
  const [persons, setPersons] = useState<Person[] | null>(null);
  const [filterText, setFilterText] = useState<string>('');
  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch('/api/persons').then((response) => {
      setPersons(response);
    });
  });

  function handleFilterTextChanged(e: any) {
    setFilterText(e.target.value);
  }

  let filteredPersons = null;
  if (persons) {
    const lowerFilterText = filterText.toLowerCase();
    filteredPersons = persons.filter(
      (p) =>
        p.type == 'COUNCIL_MEMBER' && (
        p.name.toLowerCase().includes(lowerFilterText) ||
        p.councilMember?.borough?.toLowerCase().includes(lowerFilterText))
    );
  }

  return (
    <div>
      <div className={styles.title}>Council members</div>
      <div className={styles.content}>
        {filteredPersons == null ? (
          'Loading...'
        ) : (
          <>
            <input
              type="text"
              placeholder="Search"
              value={filterText}
              className="mb-2"
              size={30}
              onChange={handleFilterTextChanged}
            />
            <Accordion defaultActiveKey={personId}>
              {filteredPersons.map((person) => (
                <Accordion.Item
                  key={person.id}
                  eventKey={person.id}
                >
                  <Accordion.Header>
                    <strong>{person.name}</strong>
                    {person.councilMember?.borough && <>&nbsp;({person.councilMember.borough})</>}
                  </Accordion.Header>
                  <LazyAccordionBody eventKey={person.id}>
                    <PersonDetailsPanel person={person} />
                  </LazyAccordionBody>
                </Accordion.Item>
              ))}
            </Accordion>
          </>
        )}
      </div>
    </div>
  );
}
