import React, { useState, useRef, ReactElement } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, BillType } from '../types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from '../useApiFetch';
import SearchCityBillsForm from './SearchCityBillsForm';
import SearchStateBillsForm from './SearchStateBillsForm';

interface Props {
  show: boolean;
  handleHide: () => void;
  handleBillTracked: () => void;
}

export default function SearchBillsModal(props: Props): ReactElement {
  const citySearchBoxRef = useRef<HTMLInputElement>(null);
  const stateCodeNameRef = useRef<HTMLInputElement>(null);
  const stateSessionYearRef = useRef<HTMLInputElement>(null);

  const [citySearchResults, setSearchResults] = useState<Bill[] | null>(null);

  const apiFetch = useApiFetch();

  const [billType, setBillType] = useState<BillType>('CITY');

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
        <Form.Check
          inline
          checked={billType === 'CITY'}
          name="type"
          label="City Council"
          value="CITY"
          type="radio"
          onChange={handleBillTypeChanged}
          id={`inline-radio-1`}
        />
        <Form.Check
          inline
          checked={billType !== 'CITY'}
          label="NY State"
          name="type"
          value="STATE"
          type="radio"
          onChange={handleBillTypeChanged}
          id={`inline-radio-2`}
        />
        {billType === 'CITY' ? (
          <SearchCityBillsForm handleBillTracked={props.handleBillTracked} />
        ) : (
          <SearchStateBillsForm handleBillTracked={props.handleBillTracked} />
        )}
      </Modal.Body>
    </Modal>
  );
}
