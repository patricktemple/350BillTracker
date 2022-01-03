import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import { Person, CouncilMember, PersonType } from './types';
import Accordion from 'react-bootstrap/Accordion';
import PersonDetailsPanel from './PersonDetailsPanel';
import { Form } from 'react-bootstrap';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';
import styles from './style/LegislatorsPage.module.scss';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

interface Props {
  persons: Person[];
  filterText: string;
  selectedPersonId?: string;
  personTypeFilter?: PersonType;
}

export default function PersonsList({
  persons,
  filterText,
  selectedPersonId,
  personTypeFilter
}: Props) {
  let filteredPersons = null;

  const lowerFilterText = filterText.toLowerCase();
  filteredPersons = persons.filter(
    (p) =>
      (p.name.toLowerCase().includes(lowerFilterText) ||
        p.councilMember?.borough?.toLowerCase().includes(lowerFilterText)) &&
      (!personTypeFilter || p.type === personTypeFilter)
  );

  return (
    <Accordion defaultActiveKey={selectedPersonId}>
      {filteredPersons.map((person) => (
        <Accordion.Item key={person.id} eventKey={person.id}>
          <Accordion.Header>
            <strong>{person.name}</strong>
            {person.councilMember?.borough && (
              <>&nbsp;({person.councilMember.borough})</>
            )}
          </Accordion.Header>
          <LazyAccordionBody eventKey={person.id}>
            <PersonDetailsPanel person={person} />
          </LazyAccordionBody>
        </Accordion.Item>
      ))}
    </Accordion>
  );
}
