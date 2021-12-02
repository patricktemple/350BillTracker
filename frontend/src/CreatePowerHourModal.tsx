import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, CreatePowerHourResponse, PowerHour } from './types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from './useApiFetch';
import Alert from 'react-bootstrap/Alert';

import moment from 'moment';

interface Props {
  bill: Bill;
  oldPowerHours: PowerHour[];
  show: boolean;
  handlePowerHourCreated: () => void;
  onHide: () => void;
}

const DO_NOT_IMPORT_VALUE = 'none';

export default function CreatePowerHourModal(props: Props): ReactElement {
  const titleRef = useRef<HTMLInputElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);

  const [createPowerHourInProgress, setCreatePowerHourInProgress] =
    useState<boolean>(false);

  const [createPowerHourMessages, setCreatePowerHourMessages] = useState<
    string[]
  >([]);
  const [powerHourResult, setPowerHourResult] = useState<PowerHour | null>(
    null
  );

  const apiFetch = useApiFetch();

  function handleHide() {
    setCreatePowerHourMessages([]);
    setCreatePowerHourInProgress(false);
    setPowerHourResult(null);
    props.onHide();
  }

  function handleSubmit(e: any) {
    const title = titleRef.current!.value;
    const selectValue = selectRef.current!.value;
    // TODO: Controlled component?

    console.log(selectRef.current!);
    console.log({ title, selectValue });

    setCreatePowerHourInProgress(true);
    apiFetch(
      `/api/saved-bills/${props.bill.id}/create-phone-bank-spreadsheet`,
      {
        method: 'POST',
        body: {
          name: title, // TODO: Use title as name in backend too
          powerHourIdToImport:
            selectValue !== DO_NOT_IMPORT_VALUE ? selectValue : null
        }
      }
    ).then((response: CreatePowerHourResponse) => {
      setCreatePowerHourMessages(response.messages);
      setCreatePowerHourInProgress(false);
      setPowerHourResult(response.powerHour);
      props.handlePowerHourCreated();
    });

    e.preventDefault();
  }

  // TODO: Identify the latest power hour and default to it
  // Also, give a little text explanation of what is happening here

  // Maybe use React Bootstrap alert component to make the messages look better?

  const defaultTitle = `Power Hour for ${props.bill.file} (${moment().format(
    'MMM D YYYY'
  )})`; // TODO add bill name to this title

  return (
    <Modal show={props.show} onHide={handleHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Create a Power Hour</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Spreadsheet title</Form.Label>
            <Form.Control
              type="text"
              ref={titleRef}
              defaultValue={defaultTitle}
              disabled={createPowerHourInProgress || !!powerHourResult}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Copy data from previous power hour</Form.Label>
            <Form.Select
              ref={selectRef}
              disabled={
                createPowerHourInProgress ||
                !!powerHourResult ||
                props.oldPowerHours.length == 0
              }
            >
              {props.oldPowerHours.length > 0 &&
                props.oldPowerHours.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              <option value={DO_NOT_IMPORT_VALUE}>
                {props.oldPowerHours.length > 0
                  ? 'Do not import'
                  : 'This bill has no previous power hours'}
              </option>
            </Form.Select>
          </Form.Group>

          {powerHourResult ? (
            <>
              <Alert variant="primary">
                <p>
                  {createPowerHourMessages.map((m) => (
                    <div key={m}>{m}</div>
                  ))}
                </p>
                <p className="mb-0" style={{ fontWeight: 'bold' }}>
                  <a
                    href={powerHourResult.spreadsheetUrl}
                    rel="noreferrer"
                    target="_blank"
                  >
                    Open spreadsheet
                  </a>
                </p>
              </Alert>
              <Button variant="primary" className="mb-2" onClick={handleHide}>
                Close
              </Button>
            </>
          ) : (
            <Button
              variant="primary"
              type="submit"
              className="mb-2"
              disabled={createPowerHourInProgress || !!powerHourResult}
            >
              {createPowerHourInProgress
                ? 'Generating...'
                : 'Generate spreadsheet'}
            </Button>
          )}
        </Form>
      </Modal.Body>
    </Modal>
  );
}
