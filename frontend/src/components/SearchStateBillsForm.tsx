import React, { useState, useRef, ReactElement } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, BillType, StateBillSearchResult, Uuid } from '../types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from '../useApiFetch';
import DetailTable, {
  DetailLabel,
  DetailContent
} from '../components/DetailTable';
import styles from '../style/components/BillSearchResults.module.scss';

function BillRow(props: {
  bill: StateBillSearchResult;
  handleTrackBill: (bill: StateBillSearchResult) => void;
}) {
  const [trackClicked, setTrackClicked] = useState<boolean>(false);

  const { bill } = props;

  function handleTrackBill() {
    setTrackClicked(true);
    props.handleTrackBill(bill);
  }

  // Lazy way to make this UI respond to click, without better global state.
  // Assumes that tracking API call actually will work.
  return (
    <div className={styles.resultsItem}>
      <DetailTable>
        <DetailLabel>Number</DetailLabel>
        <DetailContent>{bill.basePrintNo}</DetailContent>
        <DetailLabel>Session year</DetailLabel>
        <DetailContent>{bill.sessionYear}</DetailContent>
        <DetailLabel>Chamber</DetailLabel>
        <DetailContent>{bill.chamber}</DetailContent>
        <DetailLabel>Official name</DetailLabel>
        <DetailContent>{bill.name}</DetailContent>
        <DetailLabel>Description</DetailLabel>
        <DetailContent>{bill.description}</DetailContent>
        <DetailLabel>Status</DetailLabel>
        <DetailContent>{bill.status}</DetailContent>
        <DetailLabel>Track this bill?</DetailLabel>
        <DetailContent>
          {bill.tracked || trackClicked ? (
            <Button disabled size="sm">
              Already tracked
            </Button>
          ) : (
            <Button size="sm" onClick={handleTrackBill}>
              Track
            </Button>
          )}
        </DetailContent>
      </DetailTable>
    </div>
  );
}

interface Props {
  todo?: string;
  handleBillTracked: (billId: Uuid) => void;
}

export default function SearchBillsModal(props: Props): ReactElement {
  const codeNameRef = useRef<HTMLInputElement>(null);
  const sessionYearRef = useRef<HTMLInputElement>(null);

  const [searchResults, setSearchResults] = useState<
    StateBillSearchResult[] | null
  >(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  const apiFetch = useApiFetch();

  function handleSubmit(e: any) {
    setIsSearching(true);
    const params = new URLSearchParams({
      codeName: codeNameRef.current!.value,
      sessionYear: sessionYearRef.current!.value
    });
    apiFetch('/api/state-bills/search?' + params).then((response) => {
      setIsSearching(false);
      setSearchResults(response);
    });
    e.preventDefault();
  }

  function handleTrackBill(bill: StateBillSearchResult) {
    apiFetch('/api/state-bills/track', {
      method: 'POST',
      body: { sessionYear: bill.sessionYear, basePrintNo: bill.basePrintNo }
    }).then((response) => {
      props.handleBillTracked(response.id);
    });
  }

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3 mt-3">
        <Form.Label>
          Senate or assembly bill number (such as &quot;S4264&quot; or
          &quot;A6967&quot;):
        </Form.Label>
        <Form.Control
          type="text"
          ref={codeNameRef}
          placeholder="Senate or assembly bill number"
        />
        <Form.Label className="mt-3">Session year (optional):</Form.Label>
        <Form.Control
          type="text"
          ref={sessionYearRef}
          placeholder="The year the bill was introduced"
        />
      </Form.Group>

      <Button
        variant="primary"
        type="submit"
        className="mb-2"
        disabled={isSearching}
      >
        {isSearching ? 'Searching...' : 'Search'}
      </Button>
      {searchResults != null && (
        <div className={styles.resultsContainer}>
          {searchResults.map((bill: any) => (
            <BillRow
              key={bill.id}
              bill={bill}
              handleTrackBill={handleTrackBill}
            />
          ))}
        </div>
      )}
    </Form>
  );
}
