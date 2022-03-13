import Table from 'react-bootstrap/Table';
import { Bill } from '../types';
import Button from 'react-bootstrap/Button';
import React, { useState } from 'react';
import DetailTable, {
  DetailLabel,
  DetailContent
} from '../components/DetailTable';
import styles from '../style/components/BillSearchResults.module.scss';

interface Props {
  bills: Bill[];
  handleTrackBill: (id: number) => void;
}

function BillListRow(props: {
  bill: Bill;
  handleTrackBill: (cityBillId: number) => void;
}) {
  const [trackClicked, setTrackClicked] = useState<boolean>(false);

  const { bill } = props;
  function handleTrackBill() {
    setTrackClicked(true);
    props.handleTrackBill(bill.cityBill!.cityBillId);
  }

  // Lazy way to make this UI respond to click, without better global state.
  // Assumes that tracking API call actually will work.
  return (
    <div className={styles.resultsItem}>
      <DetailTable>
        <DetailLabel>Number</DetailLabel>
        <DetailContent>{bill.cityBill!.file}</DetailContent>
        <DetailLabel>Official name</DetailLabel>
        <DetailContent>{bill.name}</DetailContent>
        <DetailLabel>Description</DetailLabel>
        <DetailContent>{bill.description}</DetailContent>
        <DetailLabel>Status</DetailLabel>
        <DetailContent>{bill.cityBill!.status}</DetailContent>
        <DetailLabel>Council body</DetailLabel>
        <DetailContent>{bill.cityBill!.councilBody}</DetailContent>
        <DetailLabel>Track this bill?</DetailLabel>
        <DetailContent>
          <Button disabled={bill.tracked || trackClicked} size="sm" onClick={handleTrackBill}>
              <>{bill.tracked && 'Already tracked'}
              {trackClicked && 'Tracking...'}
              {!bill.tracked && !trackClicked && 'Track'}
              </>
            </Button>
        </DetailContent>
      </DetailTable>
    </div>
  );
}

export default function BillList(props: Props) {
  return (
    <div className={styles.resultsContainer}>
      {props.bills.map((bill: any) => (
        <BillListRow
          key={bill.id}
          bill={bill}
          handleTrackBill={props.handleTrackBill}
        />
      ))}
    </div>
  );
}
