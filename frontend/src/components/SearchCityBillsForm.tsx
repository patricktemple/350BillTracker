import React, { useState, useRef, ReactElement } from 'react';
import CityBillSearchResults from './CityBillSearchResults';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, BillType } from '../types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from '../useApiFetch';

interface Props {
  handleBillTracked: () => void;
}

export default function SearchCityBillsForm(props: Props): ReactElement {
  const searchBoxRef = useRef<HTMLInputElement>(null);

  const [searchResults, setSearchResults] = useState<Bill[] | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  const apiFetch = useApiFetch();

  function handleSubmit(e: any) {
    setIsSearching(true);
    const params = new URLSearchParams({
      file: searchBoxRef.current!.value
    });
    apiFetch('/api/city-bills/search?' + params).then((response) => {
      setIsSearching(false);
      setSearchResults(response);
    });
    e.preventDefault();
  }

  function handleTrackBill(cityBillId: number) {
    apiFetch('/api/city-bills/track', {
      method: 'POST',
      body: { cityBillId }
    }).then((response) => {
      props.handleBillTracked();
    });
  }

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3 mt-3">
        <Form.Label>Intro number (such as &quot;2317-2021&quot;)</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter bill number"
          ref={searchBoxRef}
        />
      </Form.Group>
      <Button variant="primary" type="submit" className="mb-2" disabled={isSearching}>
        {isSearching ? 'Searching...' : 'Search'}
      </Button>
      {searchResults != null && (
        <CityBillSearchResults
          bills={searchResults}
          handleTrackBill={handleTrackBill}
        />
      )}
    </Form>
  );
}
