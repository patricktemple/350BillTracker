import React, { ReactElement, useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect';
import SearchBillsModal from './SearchBillsModal';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import { Bill } from './types';
import BillDetails from './BillDetails';
import LazyAccordionBody from './LazyAccordionBody';
import useApiFetch from './useApiFetch';
import { ReactComponent as StateIcon } from './assets/state.svg';
import CityBillListItem from './CityBillListItem';
// TODO: Buy these icons!!!

import styles from './style/BillListPage.module.scss';
import StateBillListItem from './StateBillListItem';

interface Props {
  match: { params: { billId?: number } };
}

export default function BillListPage({
  match: {
    params: { billId }
  }
}: Props): ReactElement {
  const [bills, setBills] = useState<Bill[] | null>(null);
  const [addBillVisible, setAddBillVisible] = useState<boolean>(false);
  const apiFetch = useApiFetch();

  function loadBillList() {
    apiFetch('/api/saved-bills').then((response) => {
      setBills(response);
    });
  }

  useMountEffect(() => {
    // loadBillList();
    setBills([
      {
        id: '1234',
        name: "Climate and Community Investment Act",
        tracked: true,
        notes: '',
        nickname: '',
        type: 'STATE',
        twitterSearchTerms: [],
        cityBill: null,
        stateBill: {
          senateBill: {
            basePrintNo: 'S0462',
            status: "In Senate Committee",
            activeVersionName: 'A',
            sponsorCount: 25,
          },
          assemblyBill: null,
          sessionYear: 2021,
          summary: "Enacts the blah blah"
        }
      },
      {
        id: '1235',
        name: "Ban gas in constructino",
        tracked: true,
        notes: '',
        nickname: 'GasFreeNYC',
        type: 'CITY',
        twitterSearchTerms: [],
        cityBill: {
          file: "Int 2317-2021",
          cityBillId: 3,
          status: "Enacted",
          title: "Bans gas in construction",
          councilBody: "Committee on Environmental Protection",
          sponsorCount: 25,
        },
        stateBill: null,
      }
    ]);
  });

  function handleTrackBill(cityBillId: number) {
    apiFetch('/api/saved-bills', {
      method: 'POST',
      body: { cityBillId }
    }).then((response) => {
      loadBillList();
    });
  }

  function handleRemoveBill(billId: string) {
    apiFetch(`/api/saved-bills/` + billId, {
      method: 'DELETE'
    }).then((response) => {
      loadBillList();
    });
  }

  return (
    <div>
      <div className={styles.title}>Bills</div>
      <div className={styles.content}>
        {bills == null ? (
          'Loading...'
        ) : (
          <>
            <div style={{ textAlign: 'right' }}>
              <Button
                className="mb-2"
                onClick={() => setAddBillVisible(true)}
                size="sm"
              >
                Add a bill
              </Button>
            </div>
            <Accordion defaultActiveKey={billId?.toString()}>
              {bills.map((bill) => (
                <Accordion.Item key={bill.id} eventKey={bill.id.toString()}>
                  <Accordion.Header>
                    {bill.stateBill ? <StateBillListItem bill={bill} /> : <CityBillListItem bill={bill}/>}
                  </Accordion.Header>
                  <LazyAccordionBody eventKey={bill.id.toString()}>
                    <div>Body</div>
                    {/* <BillDetails
                      bill={bill}
                      handleRemoveBill={() => handleRemoveBill(bill.id)}
                    /> */}
                  </LazyAccordionBody>
                </Accordion.Item>
              ))}
            </Accordion>
            <SearchBillsModal
              show={addBillVisible}
              handleHide={() => setAddBillVisible(false)}
              handleTrackBill={handleTrackBill}
            />
          </>
        )}
      </div>
    </div>
  );
}
