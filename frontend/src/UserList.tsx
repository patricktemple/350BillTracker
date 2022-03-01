import React, { ReactElement, useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import { User, Uuid } from './types';
import Button from 'react-bootstrap/Button';

import styles from './style/components/UserList.module.scss';
import { ReactComponent as TrashIcon } from './assets/trash.svg';

interface Props {
  users: User[];
  handleDelete: (id: Uuid) => void;
}

export default function UserList(props: Props): ReactElement {
  const [userIdConfirmingDelete, setUserIdConfirmingDelete] =
    useState<Uuid | null>(null);

  function handleConfirmDelete(id: Uuid) {
    setUserIdConfirmingDelete(null);
    props.handleDelete(id);
  }

  return (
    <div className={styles.container}>
      <div>&nbsp;</div>
      <div className={styles.header}>Name</div>
      <div className={styles.header}>Email</div>
      {props.users.map((user) => (
        <>
          {user.canBeDeleted ? (
            <TrashIcon onClick={() => setUserIdConfirmingDelete(user.id)} />
          ) : (
            <div />
          )}
          <div>{user.name}</div>
          <div>{user.email}</div>
        </>
      ))}
      <Modal
        show={!!userIdConfirmingDelete}
        onHide={() => setUserIdConfirmingDelete(null)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Remove user?</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to remove this person&apos;s access to 350
          Brooklyn Bill Tracker?
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => setUserIdConfirmingDelete(null)}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={() => handleConfirmDelete(userIdConfirmingDelete!)}
          >
            Remove
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
