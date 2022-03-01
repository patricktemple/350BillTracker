import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from '../components/SearchBillsModal';
import Button from 'react-bootstrap/Button';
import { Bill } from '../types';
import useApiFetch from '../useApiFetch';
import PageHeader from '../components/PageHeader';

import styles from '../style/pages/BillListPage.module.scss';
import BillListItem from '../components/BillListItem';

export default function BillListPage(): ReactElement {
  const [bills, setBills] = useState<Bill[] | null>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);
  const apiFetch = useApiFetch();

  function loadBillList() {
    apiFetch('/api/bills').then((response) => {
      setBills(response);
    });
  }

  useMountEffect(() => {
    loadBillList();
  });

  return (
    <div>
      <PageHeader>Bills</PageHeader>
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
              {bills.map((bill) => (
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
