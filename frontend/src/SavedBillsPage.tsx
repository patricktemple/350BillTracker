import React, { ReactElement, useState, useContext, useEffect } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import AccordionContext from 'react-bootstrap/AccordionContext';
import { Bill } from './types';
import BillDetails from './BillDetails';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';

interface Props {
  match: { params: { billId?: number } };
}

export default function SavedBillsPage({
  match: {
    params: { billId }
  }
}: Props) {
  const [bills, setBills] = useState<Bill[] | null>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);

  const apiFetch = useApiFetch();

  function loadBillList() {
    apiFetch('/api/saved-bills')
      .then((response) => response.json())
      .then((response) => {
        setBills(response);
      });
  }

  useMountEffect(() => {
    loadBillList();
  });

  function handleTrackBill(id: number) {
    apiFetch('/api/saved-bills', {
      method: 'POST',
      body: JSON.stringify({ id }),
    })
      .then((response) => response.json())
      .then((response) => {
        loadBillList();
      });
  }

  function handleRemoveBill(billId: number) {
    apiFetch(`/api/saved-bills/` + billId, {
      method: 'DELETE',
    })
      .then((response) => response.json())
      .then((response) => {
        loadBillList();
      });
  }

  if (bills) {
    return (
      <div>
        <h3 className="mb-1">Bill campaigns</h3>
        <div style={{ textAlign: 'right' }}>
          <Button
            className="mb-2"
            onClick={() => setAddBillVisible(true)}
            size="sm"
          >
            Add a bill
          </Button>
        </div>
        <Accordion defaultActiveKey={billId?.toString()}>
          {bills.map((bill) => (
            <Accordion.Item key={bill.id} eventKey={bill.id.toString()}>
              <Accordion.Header>
                <strong>{bill.nickname || bill.name}</strong>&nbsp;({bill.file})
              </Accordion.Header>
              <LazyAccordionBody eventKey={bill.id.toString()}>
                <BillDetails
                  bill={bill}
                  handleRemoveBill={() => handleRemoveBill(bill.id)}
                />
              </LazyAccordionBody>
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
