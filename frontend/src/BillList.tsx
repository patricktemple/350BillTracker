import Table from 'react-bootstrap/Table';
import { Bill } from './types';
import Button from 'react-bootstrap/Button';
import React from 'react';

interface Props {
  bills: Bill[];
  showSaveBill?: boolean;
  onBillSaved?: (id: number) => void;
}

export default function BillList(props: Props) {
    return (
        <Table striped bordered>
          <thead>
            <tr>
              <th>
                File
              </th>
              <th>Name</th>
              <th>Title</th>
              <th>Status</th>
              <th>Body</th>
              {props.showSaveBill && <th>Saved?</th>}
            </tr>
          </thead>
          <tbody>
            {props.bills.map((bill: any) => (
              <tr key={bill.id}>
                <td>{bill.file}</td>
                <td>{bill.name}</td>
                <td>{bill.title}</td>
                <td>{bill.status}</td>
                <td>{bill.body}</td>
                {props.showSaveBill && props.onBillSaved && <td><Button size="sm" onClick={() => props.onBillSaved!(bill.id)}>Track this bill</Button></td>}
              </tr>
            ))}
          </tbody>
        </Table>
      );
}