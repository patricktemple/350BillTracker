import { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import Table from 'react-bootstrap/Table';
import './App.css';

function App() {
  const [bills, setBills] = useState<any>(null);
  useMountEffect(() => {
    fetch("/bills")
      .then(response => response.json())
      .then(response => {
        setBills(response);
    });
  });

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
        {bills && bills.map((bill: any) => (
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

export default App;
