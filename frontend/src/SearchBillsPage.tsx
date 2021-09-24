import { useState, useRef } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill } from './types';
import './App.css';

export default function SearchBillsPage() {
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

    function onBillSaved(id: number) {
        fetch("/saved-bills", {
            method: "POST",
            body: JSON.stringify({ id }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => response.json()).then(response => {
            window.alert("Bill saved!");
        });
    }

   return (<div><Form>
        <Form.Group className="mb-3" controlId="formBasicEmail">
            <Form.Label>Intro number (such as "2317-2021")</Form.Label>
            <Form.Control type="text" placeholder="Enter bill number" ref={searchBoxRef} />
        </Form.Group>

        <Button variant="primary" onClick={onSearchClicked}>
            Search
        </Button>
    </Form>
    {searchResults != null && <BillList bills={searchResults} showSaveBill={true} onBillSaved={onBillSaved} />}
    </div>);
}
