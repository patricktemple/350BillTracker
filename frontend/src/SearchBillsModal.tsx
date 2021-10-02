import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill } from './types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from './useApiFetch';

interface Props {
  show: boolean;
  handleHide: () => void;
  handleTrackBill: (id: number) => void;
}

export default function SearchBillsModal(props: Props): ReactElement {
  const searchBoxRef = useRef<HTMLInputElement>(null);

  const [searchResults, setSearchResults] = useState<Bill[] | null>(null);

  const apiFetch = useApiFetch();

  function handleSubmit(e: any) {
    const searchText = searchBoxRef.current!.value;
    const params = new URLSearchParams({
      file: searchText
    });
    apiFetch('/api/search-bills?' + params)
      .then((response) => response.json())
      .then((response) => {
        setSearchResults(response);
      });
    e.preventDefault();
  }

  function handleHide() {
    setSearchResults(null);
    props.handleHide();
  }

  return (
    <Modal show={props.show} onHide={handleHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Look up a bill from legislative data</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>
              Intro number (such as &quot;2317-2021&quot;)
            </Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter bill number"
              ref={searchBoxRef}
            />
          </Form.Group>

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
