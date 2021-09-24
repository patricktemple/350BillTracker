import React, { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import './App.css';

export default function SavedBillsPage() {
  const [bills, setBills] = useState<any>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);

  function loadBillList() {
    fetch("/api/saved-bills")
        .then(response => response.json())
        .then(response => {
        setBills(response);
    });
  }

  useMountEffect(() => {
    loadBillList();
  });

  function handleBillSaved(id: number) {
    fetch("/api/saved-bills", {
        method: "POST",
        body: JSON.stringify({ id }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json()).then(response => {
        loadBillList();
    });
}

  if (bills) {
    return (
        <div>
          <Button onClick={() => setAddBillVisible(true)}>Add a bill</Button>
          <BillList bills={bills} />
          <SearchBillsModal show={addBillVisible} onHide={() => setAddBillVisible(false)} handleBillSaved={handleBillSaved} />
        </div>
    )
  }
  return <div>Loading...</div>;
}
