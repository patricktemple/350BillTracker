import React, { useState } from 'react';
import styles from '../style/pages/PersonsPage.module.scss';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import PersonsList from '../components/PersonsList';
import PageHeader from '../components/PageHeader';

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
      <PageHeader>People</PageHeader>
      <div className={styles.content}>
        <input
          type="text"
          placeholder="Type name to search"
          value={filterText}
          className={styles.searchBox}
          size={30}
          onChange={handleFilterTextChanged}
        />
        <Tabs className="mt-2" unmountOnExit={true}>
          <Tab eventKey="all" title="All">
            <PersonsList filterText={filterText} selectedPersonId={personId} />
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
