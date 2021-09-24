import { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import BillList from './BillList';
import './App.css';

export default function LookupBillPage() {
//   const [bills, setBills] = useState<any>(null);
//   useMountEffect(() => {
//     fetch("/bills")
//       .then(response => response.json())
//       .then(response => {
//         setBills(response);
//     });
//   });

//   if (bills) {
//     return <BillList bills={bills} />
//   }
  return <div>Look up a bill!</div>;
}
