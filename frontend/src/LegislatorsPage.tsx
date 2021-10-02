import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import { Legislator } from './types';
import Accordion from 'react-bootstrap/Accordion';
import LegislatorDetailsPanel from './LegislatorDetailsPanel';
import { Form } from 'react-bootstrap';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';

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
  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch('/api/legislators')
      .then((response) => response.json())
      .then((response) => {
        setLegislators(response);
      });
  });

  function handleFilterTextChanged(e: any) {
    setFilterText(e.target.value);
  }

  if (legislators) {
    const lowerFilterText = filterText.toLowerCase();
    const filteredLegislators = legislators.filter(
      (l) =>
        l.name.toLowerCase().includes(lowerFilterText) ||
        l.borough?.toLowerCase().includes(lowerFilterText)
    );
    return (
      <div>
        <h3 className="mb-4">Council members</h3>
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
      </div>
    );
  }
  return <div>Loading...</div>;
}
