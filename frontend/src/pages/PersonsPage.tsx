import React, { useState } from 'react';
import styles from '../style/pages/PersonsPage.module.scss';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import PersonsList from '../components/PersonsList';
import PageHeader from '../components/PageHeader';
import SearchBox from '../components/SearchBox';
import { PersonType } from '../types';
import Dropdown from 'react-bootstrap/Dropdown';

interface Props {
  match: { params: { personId?: string } };
}

type PersonTypeFilter = PersonType | 'ALL';

const mobileDropdownText = {
  'ALL': "all people",
  'COUNCIL_MEMBER': 'council members',
  'SENATOR': 'senators',
  "ASSEMBLY_MEMBER": 'assembly members',
  "STAFFER": "staffers"
}

export default function PersonsPage({
  match: {
    params: { personId }
  }
}: Props) {
  const [filterText, setFilterText] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<PersonTypeFilter>('ALL');

  function handleFilterTextChanged(text: string) {
    setFilterText(text);
  }

  function handleTabSelect(key: any) {
    setTypeFilter(key as PersonTypeFilter);
  }
  return (
    <div>
      <PageHeader>People</PageHeader>
      <div className={styles.content}>
        <SearchBox
          onChange={handleFilterTextChanged}
          placeholder="Search by name"
        />
        <Tabs className={`mt-2 ${styles.desktopTabs}`} unmountOnExit={true} onSelect={handleTabSelect} >
          <Tab eventKey={'ALL'} title="All" />
          <Tab eventKey={'COUNCIL_MEMBER'} title="Council members" />
          <Tab eventKey={'SENATOR'} title="Senators" />
          <Tab eventKey={'ASSEMBLY_MEMBER'} title="Assembly members" />
          <Tab eventKey={'STAFFER'} title="Staffers" />
        </Tabs>
        <div className={styles.mobileDropdownContainer}>
                <Dropdown onSelect={handleTabSelect}>
        <Dropdown.Toggle variant="success" className={styles.mobileDropdown}>
           Show <a href="#">{mobileDropdownText[typeFilter]}</a>
        </Dropdown.Toggle>

        <Dropdown.Menu>
          <Dropdown.Item eventKey="ALL">All people</Dropdown.Item>
          <Dropdown.Item eventKey="COUNCIL_MEMBER">City council members</Dropdown.Item>
          <Dropdown.Item eventKey="SENATOR">State senators</Dropdown.Item>
          <Dropdown.Item eventKey="ASSEMBLY_MEMBER">State assembly members</Dropdown.Item>
          <Dropdown.Item eventKey="STAFFER">Staffers</Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
        </div>
        <PersonsList
              filterText={filterText}
              selectedPersonId={personId}
              personTypeFilter={typeFilter === 'ALL' ? undefined : typeFilter}
            />
      </div>
    </div>
  );
}
