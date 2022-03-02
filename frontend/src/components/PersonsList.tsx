import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import { Person, CouncilMember, PersonType } from '../types';
import Accordion from 'react-bootstrap/Accordion';
import PersonDetailsPanel from './PersonDetailsPanel';
import { Form } from 'react-bootstrap';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from '../useApiFetch';
import styles from '../style/components/PersonsList.module.scss';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

interface Props {
  filterText: string;
  selectedPersonId?: string;
  personTypeFilter?: PersonType;
}

function getPersonDetail(person: Person, displayPersonType: boolean) {
  if (displayPersonType) {
    if (person.type === 'COUNCIL_MEMBER' && person.councilMember?.borough) {
      return `(City Council, ${person.councilMember.borough})`;
    }
    if (person.type === 'COUNCIL_MEMBER') {
      return '(City Council)';
    }
    if (person.type === 'SENATOR') {
      return '(Senate)';
    }
    if (person.type === 'ASSEMBLY_MEMBER') {
      return '(Assembly)';
    }
    if (person.type === 'STAFFER') {
      return '(Staffer)';
    }
  } else if (person.councilMember?.borough) {
    return ` (${person.councilMember.borough})`;
  }
  return null;
}

export default function PersonsList({
  filterText,
  selectedPersonId,
  personTypeFilter
}: Props) {
  const apiFetch = useApiFetch();
  const [persons, setPersons] = useState<Person[] | null>(null);

  useMountEffect(() => {
    apiFetch('/api/persons').then((response) => {
      setPersons(response);
    });
  });

  if (persons == null) {
    return <div>Loading...</div>;
  }

  const lowerFilterText = filterText.toLowerCase();
  const filteredPersons = persons?.filter(
    (p) =>
      (p.name.toLowerCase().includes(lowerFilterText) ||
        p.councilMember?.borough?.toLowerCase().includes(lowerFilterText)) &&
      (!personTypeFilter || p.type === personTypeFilter)
  );

  return (
    <Accordion defaultActiveKey={selectedPersonId}>
      {filteredPersons.map((person) => (
        <Accordion.Item key={person.id} eventKey={person.id}>
          <Accordion.Header className={styles.accordionItem}>
            <strong>{person.name}</strong>
            &nbsp;{getPersonDetail(person, personTypeFilter == null)}
          </Accordion.Header>
          <LazyAccordionBody eventKey={person.id}>
            <PersonDetailsPanel person={person} />
          </LazyAccordionBody>
        </Accordion.Item>
      ))}
    </Accordion>
  );
}
