import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import { Person } from './types';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';
import styles from './style/LegislatorsPage.module.scss';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import PersonsList from './PersonsList';

interface Props {
  match: { params: { personId?: string } };
}

export default function PersonsPage({
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

  return (
    <div>
      <div className={styles.title}>People</div>
      <div className={styles.content}>
        <input
          type="text"
          placeholder="Type name to search"
          value={filterText}
          className="mb-2"
          size={30}
          onChange={handleFilterTextChanged}
        />
        {persons == null ? (
          'Loading...'
        ) : (
          <Tabs className="mb-4">
            <Tab eventKey="all" title="All">
              <PersonsList
                persons={persons}
                filterText={filterText}
                selectedPersonId={personId}
              />
            </Tab>
            <Tab eventKey="council" title="Council members">
              <PersonsList
                persons={persons}
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'COUNCIL_MEMBER'}
              />
            </Tab>
            <Tab eventKey="senate" title="Senators">
              <PersonsList
                persons={persons}
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'SENATOR'}
              />
            </Tab>
            <Tab eventKey="assembly" title="Assembly members">
              <PersonsList
                persons={persons}
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'ASSEMBLY_MEMBER'}
              />
            </Tab>
            <Tab eventKey="staffers" title="Staffers">
              <PersonsList
                persons={persons}
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'STAFFER'}
              />
            </Tab>
          </Tabs>
        )}
      </div>
    </div>
  );
}
