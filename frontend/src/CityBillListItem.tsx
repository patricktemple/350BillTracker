import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill, StateChamberBill } from './types';
import useApiFetch from './useApiFetch';
import { ReactComponent as CityIcon } from './assets/city.svg';
// TODO: Buy these icons!!!

interface Props {
  bill: Bill;
}

export default function CityBillListItem({ bill }: Props) {
  // TODO: Don't wrap this in <>, use a self-contained proper layout
  const cityBill = bill.cityBill!;
  return (
    <>
      <CityIcon
        style={{ width: '60px', height: '60px', marginRight: '10px' }}
      />
      <div>
        <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
          {bill.nickname || bill.name}
        </div>
        <div>{cityBill.file}</div>
        <div className="mt-3">{cityBill.status}</div>
        <div>{cityBill.sponsorCount} sponsors</div>
      </div>
    </>
  );
}
