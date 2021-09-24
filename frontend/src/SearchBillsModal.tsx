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
    onHide: () => void;
    handleBillSaved: (id: number) => void;
}

export default function SearchBillsModal(props: Props) {
    const searchBoxRef = useRef<HTMLInputElement>(null);

    const [searchResults, setSearchResults] = useState<Bill[] | null>(null);

    function onSearchClicked() {
        const searchText = searchBoxRef.current!.value;
        const params = new URLSearchParams({
            file: searchText
        });
        fetch("/search-bills?" + params).then(response => response.json()).then(response => {
            setSearchResults(response);
        });
    }

    function handleHide() {
        setSearchResults(null);
        props.onHide()
    }

    // TODO: Handle Enter key (submit button?)
   return (<Modal show={props.show} onHide={handleHide} size="xl">
       <Modal.Header closeButton>
           <Modal.Title>Lookup a bill</Modal.Title>
        </Modal.Header>
        <Modal.Body>
       <Form>
        <Form.Group className="mb-3">
            <Form.Label>Intro number (such as &quot;2317-2021&quot;)</Form.Label>
            <Form.Control type="text" placeholder="Enter bill number" ref={searchBoxRef} />
        </Form.Group>

        <Button variant="primary" onClick={onSearchClicked}>
            Search
        </Button>
    </Form>
    {searchResults != null && <BillList bills={searchResults} showSaveBill={true} onBillSaved={props.handleBillSaved} />}
    </Modal.Body>
    </Modal>);
}
