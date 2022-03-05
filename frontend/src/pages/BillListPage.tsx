import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from '../components/SearchBillsModal';
import Button from 'react-bootstrap/Button';
import { Bill } from '../types';
import useApiFetch from '../useApiFetch';
import PageHeader from '../components/PageHeader';

import styles from '../style/pages/BillListPage.module.scss';
import BillListItem from '../components/BillListItem';
import SearchBox from '../components/SearchBox';

export default function BillListPage(): ReactElement {
  const [bills, setBills] = useState<Bill[] | null>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);
  const apiFetch = useApiFetch();
  const [filterText, setFilterText] = useState<string>('');

  function loadBillList() {
    apiFetch('/api/bills').then((response) => {
      setBills(response);
    });
  }

  useMountEffect(() => {
    loadBillList();
  });

  function handleFilterTextChanged(text: string) {
    setFilterText(text);
  }

  const lowerFilterText = filterText.toLowerCase();
  const filteredBills =
    bills == null
      ? null
      : bills.filter(
          (bill) =>
            bill.displayName.toLowerCase().includes(lowerFilterText) ||
            bill.codeName.toLowerCase().includes(lowerFilterText)
        );

  return (
    <div>
      <PageHeader>Bills</PageHeader>
      <div className={styles.content}>
        {filteredBills == null ? (
          'Loading...'
        ) : (
          <>
            <div className={styles.topControls}>
              <SearchBox
                onChange={handleFilterTextChanged}
                placeholder="Search by name or number"
              />
              <Button
                className={styles.addBillButton}
                onClick={() => setAddBillVisible(true)}
                size="sm"
              >
                Add a bill
              </Button>
            </div>
            <div className={styles.billList}>
              {filteredBills.map((bill) => (
                <BillListItem bill={bill} key={bill.id} />
              ))}
            </div>
            <SearchBillsModal
              show={addBillVisible}
              handleHide={() => setAddBillVisible(false)}
              handleBillTracked={loadBillList}
            />
          </>
        )}
      </div>
    </div>
  );
}
