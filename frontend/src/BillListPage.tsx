import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill } from './types';
import BillDetails from './BillDetailsPage';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';
import { ReactComponent as StateIcon } from './assets/state.svg';
import CityBillListItem from './CityBillListItem';
import { useHistory } from 'react-router-dom';
// TODO: Buy these icons!!!

import styles from './style/BillListPage.module.scss';
import StateBillListItem from './StateBillListItem';

export default function BillListPage(): ReactElement {
  const [bills, setBills] = useState<Bill[] | null>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);
  const apiFetch = useApiFetch();

  function loadBillList() {
    apiFetch('/api/saved-bills').then((response) => {
      setBills([
        ...response,
        {
          id: '1234',
          name: 'Climate and Community Investment Act',
          tracked: true,
          notes: '',
          nickname: '',
          type: 'STATE',
          twitterSearchTerms: [],
          cityBill: null,
          stateBill: {
            senateBill: {
              basePrintNo: 'S0462',
              status: 'In Senate Committee',
              activeVersionName: 'A',
              sponsorCount: 25
            },
            assemblyBill: null,
            sessionYear: 2021,
            summary: 'Enacts the blah blah'
          }
        }
      ]);
    });
  }

  useMountEffect(() => {
    loadBillList();
  });

  function handleTrackBill(cityBillId: number) {
    apiFetch('/api/saved-bills', {
      method: 'POST',
      body: { cityBillId }
    }).then((response) => {
      loadBillList();
    });
  }

  // TODO: Unify the way I do different kinds of styles
  // and get rid of the bootstrap grid thing? simplify it with CSS grid

  return (
    <div>
      <div className={styles.title}>Bills</div>
      <div className={styles.content}>
        {bills == null ? (
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
            <div className={styles.billList}>
              {bills.map((bill) => <>{
                bill.stateBill ? (
                  <StateBillListItem bill={bill} />
                ) : (
                  <CityBillListItem bill={bill} />
                )
              }</>)}
            </div>
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
