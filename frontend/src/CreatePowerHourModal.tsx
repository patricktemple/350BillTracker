import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, PowerHour } from './types';
import Modal from 'react-bootstrap/Modal';

interface Props {
  oldPowerHours: PowerHour[];
  show: boolean;
  handleCreatePowerHour: (
    description: string,
    oldPowerHourId: string | null
  ) => void;
  onHide: () => void;
}

export default function CreatePowerHourModal(props: Props): ReactElement {
  const descriptionRef = useRef<HTMLInputElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);

  function handleSubmit(e: any) {
    const description = descriptionRef.current!.value;
    const selectValue = selectRef.current!.value;
    // TODO: Controlled component?

    console.log({ description, selectValue });
    props.handleCreatePowerHour(description, selectValue);
    e.preventDefault();
  }

  // TODO: Identify the latest power hour and default to it

  return (
    <Modal show={props.show} onHide={props.onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Create a Power Hour</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control
              type="text"
              ref={descriptionRef}
              defaultValue="Power Hour TODO name this"
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Import from previous power hour</Form.Label>
            <Form.Select ref={selectRef}>
              {props.oldPowerHours.map((p) => (
                <option key={p.id}>{p.name}</option>
              ))}
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
