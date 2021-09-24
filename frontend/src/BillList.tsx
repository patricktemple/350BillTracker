import Table from 'react-bootstrap/Table';
import { Bill } from './types';
import Button from 'react-bootstrap/Button';
import React from 'react';

interface Props {
  bills: Bill[];
  handleTrackBill: (id: number) => void;
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
              <th>Tracking</th>
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
                <td>{bill.tracked ? <Button disabled size="sm">Tracked</Button> : <Button size="sm" onClick={() => props.handleTrackBill(bill.id)}>Track this bill</Button>}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      );
}