import React from 'react';
import { Bill } from './types';
import { ReactComponent as CityIcon } from './assets/city.svg';
import styles from './style/components/BillListItem.module.scss';
import { useHistory } from 'react-router-dom';

interface Props {
  bill: Bill;
}

export default function CityBillListItem({ bill }: Props) {
  const history = useHistory();
  const cityBill = bill.cityBill!;
  return (
    <div
      className={styles.itemContainer}
      onClick={() => history.push(`/bills/${bill.id}`)}
    >
      <CityIcon className={styles.billTypeIcon} />
      <div className={styles.billDetails}>
        <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
          {bill.displayName}
        </div>
        <div>{cityBill.file}</div>
        <div className="mt-3">{cityBill.status}</div>
        <div>{cityBill.sponsorCount} sponsors</div>
      </div>
    </div>
  );
}
