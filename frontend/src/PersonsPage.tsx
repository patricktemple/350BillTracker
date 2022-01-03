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
  const [filterText, setFilterText] = useState<string>('');

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
        <Tabs className="mb-4" unmountOnExit={true}>
            <Tab eventKey="all" title="All">
              <PersonsList
                filterText={filterText}
                selectedPersonId={personId}
              />
            </Tab>
            <Tab eventKey="council" title="Council members">
              <PersonsList
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'COUNCIL_MEMBER'}
              />
            </Tab>
            <Tab eventKey="senate" title="Senators">
              <PersonsList
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'SENATOR'}
              />
            </Tab>
            <Tab eventKey="assembly" title="Assembly members">
              <PersonsList
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'ASSEMBLY_MEMBER'}
              />
            </Tab>
            <Tab eventKey="staffers" title="Staffers">
              <PersonsList
                filterText={filterText}
                selectedPersonId={personId}
                personTypeFilter={'STAFFER'}
              />
            </Tab>
          </Tabs>
      </div>
    </div>
  );
}
