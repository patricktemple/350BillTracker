import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill } from './types';
import './App.css';

export default function SavedBillsPage() {
  const [bills, setBills] = useState<Bill[] | null>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);

  function loadBillList() {
    fetch('/api/saved-bills')
      .then((response) => response.json())
      .then((response) => {
        setBills(response);
      });
  }

  useMountEffect(() => {
    loadBillList();
  });

  function handleTrackBill(id: number) {
    fetch('/api/saved-bills', {
      method: 'POST',
      body: JSON.stringify({ id }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((response) => {
        loadBillList();
      });
  }

  if (bills) {
    return (
      <div>
        <Button className="mb-2" onClick={() => setAddBillVisible(true)}>
          Add a bill
        </Button>
        <Accordion>
          {bills.map((bill) => (
            <Accordion.Item key={bill.id} eventKey={bill.id.toString()}>
              <Accordion.Header>
                <strong>{bill.name}</strong>&nbsp;({bill.file})
              </Accordion.Header>
              <Accordion.Body>{bill.title}</Accordion.Body>
            </Accordion.Item>
          ))}
        </Accordion>
        <SearchBillsModal
          show={addBillVisible}
          handleHide={() => setAddBillVisible(false)}
          handleTrackBill={handleTrackBill}
        />
      </div>
    );
  }
  return <div>Loading...</div>;
}
