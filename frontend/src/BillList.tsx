import Table from 'react-bootstrap/Table';
import { Bill } from './types';
import Button from 'react-bootstrap/Button';
import React, { useState } from 'react';

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
    <tr key={bill.cityBill!.cityBillId}>
      <td>{bill.cityBill!.file}</td>
      <td>{bill.name}</td>
      <td>{bill.cityBill!.title}</td>
      <td>{bill.cityBill!.status}</td>
      <td>{bill.cityBill!.councilBody}</td>
      <td>
        {bill.tracked || trackClicked ? (
          <Button disabled size="sm">
            Tracked
          </Button>
        ) : (
          <Button size="sm" onClick={handleTrackBill}>
            Track
          </Button>
        )}
      </td>
    </tr>
  );
}

export default function BillList(props: Props) {
  return (
    <Table striped bordered>
      <thead>
        <tr>
          <th>File</th>
          <th>Name</th>
          <th>Title</th>
          <th>Status</th>
          <th>Body</th>
          <th>Are we tracking this bill?</th>
        </tr>
      </thead>
      <tbody>
        {props.bills.map((bill: any) => (
          <BillListRow
            key={bill.id}
            bill={bill}
            handleTrackBill={props.handleTrackBill}
          />
        ))}
      </tbody>
    </Table>
  );
}
