import React, { useState, useRef, ReactElement } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, BillType, StateBillSearchResult } from './types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from './useApiFetch';
import SearchCityBillsForm from './SearchCityBillsForm';
import Table from 'react-bootstrap/Table';

function BillRow(props: {
  bill: StateBillSearchResult;
  handleTrackBill: (bill: StateBillSearchResult) => void;
}) {
  const [trackClicked, setTrackClicked] = useState<boolean>(false);

  const { bill } = props;

  function handleTrackBill() {
    setTrackClicked(true);
    props.handleTrackBill(bill);
  }

  // Lazy way to make this UI respond to click, without better global state.
  // Assumes that tracking API call actually will work.
  return (
    <tr key={bill.basePrintNo}>
      <td>{bill.basePrintNo}</td>
      <td>{bill.sessionYear}</td>
      <td>{bill.chamber}</td>
      <td>{bill.name}</td>
      <td>{bill.description}</td>
      <td>{bill.status}</td>
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

interface Props {
  todo?: string;
  //   show: boolean;
  // tood figure out session ear string or number
  handleBillTracked: () => void;
}

export default function SearchBillsModal(props: Props): ReactElement {
  const codeNameRef = useRef<HTMLInputElement>(null);
  const sessionYearRef = useRef<HTMLInputElement>(null);

  const [searchResults, setSearchResults] = useState<
    StateBillSearchResult[] | null
  >(null);

  const apiFetch = useApiFetch();

  function handleSubmit(e: any) {
    const params = new URLSearchParams({
      codeName: codeNameRef.current!.value,
      sessionYear: sessionYearRef.current!.value
    });
    apiFetch('/api/state-bills/search?' + params).then((response) => {
      setSearchResults(response);
    });
    e.preventDefault();
  }

  function handleTrackBill(bill: StateBillSearchResult) {
    apiFetch('/api/state-bills/track', {
      method: 'POST',
      body: { sessionYear: bill.sessionYear, basePrintNo: bill.basePrintNo }
    }).then((response) => {
      props.handleBillTracked();
    });
  }

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3 mt-3">
        <Form.Label>
          Senate or assembly bill number (such as &quot;S4264&quot; or
          &quot;A6967&quot;):
        </Form.Label>
        <Form.Control
          type="text"
          ref={codeNameRef}
          placeholder="Senate or assembly bill number"
        />
        <Form.Label className="mt-3">Session year (optional):</Form.Label>
        <Form.Control
          type="text"
          ref={sessionYearRef}
          placeholder="The year the bill was introduced"
        />
      </Form.Group>

      <Button variant="primary" type="submit" className="mb-2">
        Search
      </Button>
      {searchResults != null && (
        <Table striped bordered>
          <thead>
            <tr>
              <th>Bill number</th>
              <th>Session year</th>
              <th>Chamber</th>
              <th>Title</th>
              <th>Description</th>
              <th>Status</th>
              {/* <th>Are we tracking this bill?</th> */}
            </tr>
          </thead>
          <tbody>
            {searchResults.map((bill: any) => (
              <BillRow
                key={bill.id}
                bill={bill}
                handleTrackBill={handleTrackBill}
              />
            ))}
          </tbody>
        </Table>
      )}
    </Form>
  );
}
