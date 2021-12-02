import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, PowerHour } from './types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from './useApiFetch';

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

  const apiFetch = useApiFetch();

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
    ).then(() => {
      setCreatePowerHourInProgress(false);
      props.handlePowerHourCreated();
    });

    e.preventDefault();
  }

  // TODO: Identify the latest power hour and default to it
  // Also, give a little text explanation of what is happening here

  const defaultTitle = `Power Hour - ${moment().format('MM/DD/YYYY')}`; // TODO add bill name to this title

  return (
    <Modal show={props.show} onHide={props.onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Create a Power Hour</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              ref={titleRef}
              defaultValue={defaultTitle}
              disabled={createPowerHourInProgress}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Import data from previous power hour</Form.Label>
            <Form.Select
              ref={selectRef}
              disabled={
                createPowerHourInProgress || props.oldPowerHours.length == 0
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

          <Button
            variant="primary"
            type="submit"
            className="mb-2"
            disabled={createPowerHourInProgress}
          >
            {createPowerHourInProgress
              ? 'Generating...'
              : 'Generate spreadsheet'}
          </Button>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
