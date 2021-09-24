import { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import './App.css';

export default function SavedBillsPage() {
  const [bills, setBills] = useState<any>(null);
  useMountEffect(() => {
    fetch("/saved-bills")
      .then(response => response.json())
      .then(response => {
        setBills(response);
    });
  });

  if (bills) {
    return <BillList bills={bills} />
  }
  return <div>"Loading..."</div>;
}
