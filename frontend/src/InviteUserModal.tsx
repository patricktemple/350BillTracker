import React, { ReactElement, useRef } from 'react';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

interface Props {
  show: boolean;
  onHide: () => void;
  handleInviteUser: (email: string, name: string) => void;
}

export default function InviteUserModel(props: Props): ReactElement {
  const emailRef = useRef<HTMLInputElement>(null);
  const nameRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: any) {
    const email = emailRef.current!.value;
    const name = nameRef.current!.value;
    props.handleInviteUser(email, name);
    e.preventDefault();
  }

  return (
    <Modal show={props.show} onHide={props.onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Invite user</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control type="text" ref={nameRef} />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Email address</Form.Label>
            <Form.Control type="text" ref={emailRef} />
          </Form.Group>

          <Button variant="primary" type="submit" className="mb-2">
            Invite
          </Button>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
