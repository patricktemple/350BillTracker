import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, BillType } from './types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from './useApiFetch';

interface Props {
  show: boolean;
  handleHide: () => void;
  handleTrackBill: (cityBillId: number) => void;
}

export default function SearchBillsModal(props: Props): ReactElement {
  const searchBoxRef = useRef<HTMLInputElement>(null);

  const [searchResults, setSearchResults] = useState<Bill[] | null>(null);

  const apiFetch = useApiFetch();

  const [billType, setBillType] = useState<BillType>('CITY');

  function handleSubmit(e: any) {
    const searchText = searchBoxRef.current!.value;
    const params = new URLSearchParams({
      file: searchText
    });
    apiFetch('/api/search-bills?' + params).then((response) => {
      setSearchResults(response);
    });
    e.preventDefault();
  }

  function handleHide() {
    setSearchResults(null);
    props.handleHide();
  }

  function handleBillTypeChanged(e: any) {
    setBillType(e.target.value);
  }

  return (
    <Modal show={props.show} onHide={handleHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Look up a bill from legislative data</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Check
          inline
          checked={billType === 'CITY'}
          name="type"
          label="City Council"
          value="CITY"
          type='radio'
          onChange={handleBillTypeChanged}
          id={`inline-radio-1`}
          />
          <Form.Check
            inline
            checked={billType !== 'CITY'}
            label="NY State"
            name="type"
            value="STATE"
            type='radio'
            onChange={handleBillTypeChanged}
            id={`inline-radio-2`}
          />
          {billType==='CITY' ? (
          <Form.Group className="mb-3 mt-3">
            <Form.Label>
              Intro number (such as &quot;2317-2021&quot;)
            </Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter bill number"
              ref={searchBoxRef}
            />
          </Form.Group>
          ):           <Form.Group className="mb-3 mt-3">
          <Form.Label>
            Senate or assembly bill number (such as &quot;S4264&quot; or &quot;A6967&quot;):
          </Form.Label>
          <Form.Control
            type="text"
            placeholder="Senate or assembly bill number"
          />
           <Form.Label className="mt-3">
            Session year:
          </Form.Label>
          <Form.Control
            type="text"
            placeholder="The year the bill was introduced"
          />
        </Form.Group>}

          <Button variant="primary" type="submit" className="mb-2">
            Search
          </Button>
        </Form>
        {searchResults != null && (
          <>
            <div>Results (includes old historical results):</div>
            <BillList
              bills={searchResults}
              handleTrackBill={props.handleTrackBill}
            />
          </>
        )}
      </Modal.Body>
    </Modal>
  );
}
