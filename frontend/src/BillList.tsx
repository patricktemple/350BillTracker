import Table from 'react-bootstrap/Table';
import { Bill } from './types';

interface Props {
  bills: Bill[];
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
            </tr>
          </thead>
          <tbody>
            {props.bills.map((bill: any) => (
              <tr>
                <td>{bill.file}</td>
                <td>{bill.name}</td>
                <td>{bill.title}</td>
                <td>{bill.status}</td>
                <td>{bill.body}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      );
}