import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import { Legislator } from './types';
import Accordion from 'react-bootstrap/Accordion';
import LegislatorDetailsPanel from './LegislatorDetailsPanel';
import { Form } from 'react-bootstrap';
import LazyAccordionBody from './LazyAccordionBody';
import styles from './style/LegislatorsPage.module.scss';

interface Props {
  match: { params: { legislatorId?: number } };
}

export default function ConcilMembersPage({
  match: {
    params: { legislatorId }
  }
}: Props) {
  const [legislators, setLegislators] = useState<Legislator[] | null>(null);
  const [filterText, setFilterText] = useState<string>('');

  useMountEffect(() => {
    fetch('/api/legislators')
      .then((response) => response.json())
      .then((response) => {
        setLegislators(response);
      });
  });

  function handleFilterTextChanged(e: any) {
    setFilterText(e.target.value);
  }

  let filteredLegislators = null;
  if (legislators) {
    const lowerFilterText = filterText.toLowerCase();
    filteredLegislators = legislators.filter(
      (l) =>
        l.name.toLowerCase().includes(lowerFilterText) ||
        l.borough?.toLowerCase().includes(lowerFilterText)
    );
  }

  return (
    <div>
      <div className={styles.title}>Council members</div>
      <div className={styles.content}>
        {filteredLegislators == null ? (
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
            <Accordion defaultActiveKey={legislatorId?.toString()}>
              {filteredLegislators.map((legislator) => (
                <Accordion.Item
                  key={legislator.id}
                  eventKey={legislator.id.toString()}
                >
                  <Accordion.Header>
                    <strong>{legislator.name}</strong>
                    {legislator.borough && <>&nbsp;({legislator.borough})</>}
                  </Accordion.Header>
                  <LazyAccordionBody eventKey={legislator.id.toString()}>
                    <LegislatorDetailsPanel legislator={legislator} />
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
