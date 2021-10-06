import React, { useState, useRef, ReactElement } from 'react';
import BillList from './BillList';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill } from './types';
import Modal from 'react-bootstrap/Modal';

interface Props {
  show: boolean;
  handleAddStaffer: (
    name: string,
    title: string,
    phone: string,
    email: string,
    twitter: string
  ) => void;
  onHide: () => void;
}

export default function AddAttachmentModal(props: Props): ReactElement {
  const nameRef = useRef<HTMLInputElement>(null);
  const titleRef = useRef<HTMLInputElement>(null);
  const phoneRef = useRef<HTMLInputElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);
  const twitterRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: any) {
    const name = nameRef.current!.value;
    const title = titleRef.current!.value;
    const phone = phoneRef.current!.value;
    const email = emailRef.current!.value;
    const twitter = twitterRef.current!.value;
    props.handleAddStaffer(name, title, phone, email, twitter);
    e.preventDefault();
  }

  return (
    <Modal show={props.show} onHide={props.onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Add a staffer</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control type="text" ref={nameRef} />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Title</Form.Label>
            <Form.Control type="text" ref={titleRef} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Phone</Form.Label>
            <Form.Control type="text" ref={phoneRef} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Email</Form.Label>
            <Form.Control type="text" ref={emailRef} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Twitter</Form.Label>
            <Form.Control type="text" ref={twitterRef} />
          </Form.Group>

          <Button variant="primary" type="submit" className="mb-2">
            Add
          </Button>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
