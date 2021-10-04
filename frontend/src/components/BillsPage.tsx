import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill } from '../types';
import BillDetails from './BillDetails';
import LazyAccordionBody from './LazyAccordionBody';

import styles from '../style/BillsPage.module.scss';

interface Props {
  match: { params: { billId?: number } };
}

export default function SavedBillsPage({
  match: {
    params: { billId }
  }
}: Props): ReactElement {
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

  function handleRemoveBill(billId: number) {
    fetch(`/api/saved-bills/` + billId, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((response) => {
        loadBillList();
      });
  }

  return (
    <div>
      <div className={styles.title}>Bills</div>
      <div className={styles.content}>
        {!bills ? (
          'Loading...'
        ) : (
          <>
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
                    <strong>{bill.nickname || bill.name}</strong>&nbsp;(
                    {bill.file})
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
          </>
        )}
      </div>
    </div>
  );
}
