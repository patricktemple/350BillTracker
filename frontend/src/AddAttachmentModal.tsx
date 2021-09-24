import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill } from './types';
import Modal from 'react-bootstrap/Modal';
import './App.css';

interface Props {
  show: boolean;
  handleAddAttachment: (description: string, url: string) => void;
  onHide: () => void;
}

export default function AddAttachmentModal(props: Props): ReactElement {
  const descriptionRef = useRef<HTMLInputElement>(null);
  const urlRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: any) {
    const description = descriptionRef.current!.value;
    const url = urlRef.current!.value;
    props.handleAddAttachment(description, url);
    e.preventDefault();
  }

  return (
    <Modal show={props.show} onHide={props.onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Add an attachment</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Link description</Form.Label>
            <Form.Control type="text" ref={descriptionRef} placeholder='eg. "Power Hour tracker 8/23"' />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Link URL</Form.Label>
            <Form.Control type="text" ref={urlRef} />
          </Form.Group>

          <Button variant="primary" type="submit" className="mb-2">
            Add
          </Button>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
