import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from '../components/SearchBillsModal';
import Button from 'react-bootstrap/Button';
import { Bill } from '../types';
import useApiFetch from '../useApiFetch';
import CityBillListItem from '../components/CityBillListItem';

import styles from '../style/pages/BillListPage.module.scss';
import StateBillListItem from '../components/StateBillListItem';

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
              {bills.map((bill) => (
                <>
                  {bill.stateBill ? (
                    <StateBillListItem bill={bill} />
                  ) : (
                    <CityBillListItem bill={bill} />
                  )}
                </>
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
