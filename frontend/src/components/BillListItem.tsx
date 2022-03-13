import React from 'react';
import { Bill, StateChamberBill } from '../types';
import { ReactComponent as StateIcon } from '../assets/state.svg';
import { ReactComponent as CityIcon } from '../assets/city.svg';
import { useHistory } from 'react-router-dom';

import styles from '../style/components/BillListItem.module.scss';

interface StateChamberDetailsProps {
  chamberBill: StateChamberBill | null;
  chamberName: string;
}

function StateChamberDetails({
  chamberBill,
  chamberName
}: StateChamberDetailsProps) {
  // TODO: This info here is the same as the info shown on the bill
  // detail page. accordion. Make this a shared component?
  if (!chamberBill) {
    return <div className="mt-3">{chamberName} bill not yet introduced</div>;
  }
  return (
    <div className="mt-3">
      <h3>
        {chamberName} bill {chamberBill.basePrintNo}
      </h3>
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

  // TODO: Also show the lead sponsor of bills right here
  // TODO: Make these a Link?
  const stateBill = bill.stateBill!;
  return (
    <div className={styles.itemContainer}>
      {bill.type === 'STATE' ? (
        <StateIcon className={styles.stateIcon} />
      ) : (
        <CityIcon className={styles.cityIcon} />
      )}
      <div
        className={styles.billDetails}
        onClick={() => history.push(`/bills/${bill.id}`)}
      >
        <h2>{bill.displayName}</h2>
        {bill.type === 'STATE' ? (
          <>
            <StateChamberDetails
              chamberName="Senate"
              chamberBill={stateBill.senateBill}
            />
            <StateChamberDetails
              chamberName="Assembly"
              chamberBill={stateBill.assemblyBill}
            />
          </>
        ) : (
          <>
            <h3>{bill.cityBill?.file}</h3>
            <div className="mt-3">{bill.cityBill?.status}</div>
            <div>{bill.cityBill?.sponsorCount} sponsors</div>
          </>
        )}
      </div>
    </div>
  );
}
