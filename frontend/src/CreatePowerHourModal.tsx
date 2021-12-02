import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, PowerHour } from './types';
import Modal from 'react-bootstrap/Modal';

import moment from 'moment';

interface Props {
  oldPowerHours: PowerHour[];
  show: boolean;
  handleCreatePowerHour: (
    title: string,
    oldPowerHourId: string | null
  ) => void;
  onHide: () => void;
}

const DO_NOT_IMPORT_VALUE = "none";

export default function CreatePowerHourModal(props: Props): ReactElement {
  const titleRef = useRef<HTMLInputElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);

  function handleSubmit(e: any) {
    const title = titleRef.current!.value;
    const selectValue = selectRef.current!.value;
    // TODO: Controlled component?

    console.log(selectRef.current!);
    console.log({ title, selectValue });
    props.handleCreatePowerHour(title, selectValue !== DO_NOT_IMPORT_VALUE ? selectValue : null);
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
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Import data from previous power hour</Form.Label>
            <Form.Select ref={selectRef} disabled={props.oldPowerHours.length == 0}>
              {props.oldPowerHours.length > 0 && props.oldPowerHours.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
              <option value={DO_NOT_IMPORT_VALUE}>{props.oldPowerHours.length > 0 ? "Do not import" : "This bill has no previous power hours"}</option>
            </Form.Select>
          </Form.Group>

          <Button variant="primary" type="submit" className="mb-2">
            Generate spreadsheet
          </Button>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
