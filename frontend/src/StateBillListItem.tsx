import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill, StateChamberBill } from './types';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';
import { ReactComponent as StateIcon } from './assets/state.svg';
import { useHistory } from 'react-router-dom';

import styles from './style/BillListItem.module.scss';

interface StateChamberDetailsProps {
  chamberBill: StateChamberBill | null;
  chamberName: string;
}

function StateChamberDetails({
  chamberBill,
  chamberName
}: StateChamberDetailsProps) {
  if (!chamberBill) {
    return <div className="mt-3">{chamberName} bill not yet introduced</div>;
  }
  return (
    <div className="mt-3">
      <div style={{ fontWeight: 'bold' }}>
        {chamberName} bill {chamberBill.basePrintNo}
      </div>
      <div>{chamberBill.status}</div>
      <div>{chamberBill.sponsorCount} sponsors</div>
    </div>
  );
}

interface Props {
  bill: Bill;
}

export default function StateBillListItem({ bill }: Props) {
  const history = useHistory();

  const stateBill = bill.stateBill!;
  return (
    <div className={styles.itemContainer}>
      <StateIcon className={styles.billTypeIcon} />
      <div
        className={styles.billDetails}
        onClick={() => history.push(`/bills/${bill.id}`)}
      >
        <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
          {bill.displayName}
        </div>
        <StateChamberDetails
          chamberName="Senate"
          chamberBill={stateBill.senateBill}
        />
        <StateChamberDetails
          chamberName="Assembly"
          chamberBill={stateBill.assemblyBill}
        />
      </div>
    </div>
  );
}
