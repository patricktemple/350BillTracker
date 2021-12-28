import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill, StateChamberBill } from './types';
import useApiFetch from './useApiFetch';
import { ReactComponent as CityIcon } from './assets/city.svg';
import styles from './style/BillListItem.module.scss';
import { useHistory } from 'react-router-dom';
// TODO: Buy these icons!!!

interface Props {
  bill: Bill;
}

export default function CityBillListItem({ bill }: Props) {
  const history = useHistory();
  // TODO: Don't wrap this in <>, use a self-contained proper layout
  const cityBill = bill.cityBill!;
  return (
    <div className={styles.itemContainer} 
    onClick={() => history.push(`/bills/${bill.id}`)}>
      <CityIcon className={styles.billTypeIcon}
      />
      <div className={styles.billDetails}>
        <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
          {bill.nickname || bill.name}
        </div>
        <div>{cityBill.file}</div>
        <div className="mt-3">{cityBill.status}</div>
        <div>{cityBill.sponsorCount} sponsors</div>
      </div>
    </div>
  );
}
