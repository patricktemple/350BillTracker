import Button from 'react-bootstrap/Button';
import React from 'react';
import Modal from 'react-bootstrap/Modal';

interface Props {
  show: boolean;
  handleConfirm: () => void;
  handleCloseWithoutConfirm: () => void;
}

export default function CofirmDeleteBillModal({ show, handleConfirm, handleCloseWithoutConfirm }: Props) {
  return (
      <Modal show={show} onHide={handleCloseWithoutConfirm}>
        <Modal.Header closeButton>
          <Modal.Title>Remove bill?</Modal.Title>
        </Modal.Header>
        <Modal.Body>Removing this bill from the tracker will delete all notes on it.</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseWithoutConfirm}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleConfirm}>
            Remove bill
          </Button>
        </Modal.Footer>
      </Modal>
  );
}