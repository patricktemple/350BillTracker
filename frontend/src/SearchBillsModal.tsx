import React, { useState, useRef } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill } from './types';
import Modal from 'react-bootstrap/Modal';
import './App.css';

interface Props {
    show: boolean;
    handleHide: () => void;
    handleBillSaved: (id: number) => void;
}

export default function SearchBillsModal(props: Props) {
    const searchBoxRef = useRef<HTMLInputElement>(null);

    const [searchResults, setSearchResults] = useState<Bill[] | null>(null);

    function handleSubmit(e: any) {
        const searchText = searchBoxRef.current!.value;
        const params = new URLSearchParams({
            file: searchText
        });
        fetch("/api/search-bills?" + params).then(response => response.json()).then(response => {
            setSearchResults(response);
        });
        e.preventDefault();
    }

    function handleHide() {
        setSearchResults(null);
        props.handleHide()
    }

    // TODO: Handle Enter key (submit button?)
   return (<Modal show={props.show} onHide={handleHide} size="xl">
       <Modal.Header closeButton>
           <Modal.Title>Look up a bill from legislative data</Modal.Title>
        </Modal.Header>
        <Modal.Body>
       <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
            <Form.Label>Intro number (such as &quot;2317-2021&quot;)</Form.Label>
            <Form.Control type="text" placeholder="Enter bill number" ref={searchBoxRef} />
        </Form.Group>

        <Button variant="primary" type="submit">
            Search
        </Button>
    </Form>
    {searchResults != null && <BillList bills={searchResults} showSaveBill={true} onBillSaved={props.handleBillSaved} />}
    </Modal.Body>
    </Modal>);
}
