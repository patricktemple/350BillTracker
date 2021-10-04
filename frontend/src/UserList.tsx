import React, { ReactElement } from 'react';
import { User } from './types';

import styles from './style/UserList.module.scss';
import {ReactComponent as TrashIcon} from './assets/trash.svg';

interface Props {
  users: User[];
  handleDelete: (id: number) => void;
}

export default function UserList(props: Props): ReactElement {
  return (
    <div className={styles.container}>
      <div>&nbsp;</div>
      <div className={styles.header}>Name</div>
      <div className={styles.header}>Email</div>
      {props.users.map(user => (
        <>
          <TrashIcon onClick={() => props.handleDelete(user.id)}/>
          <div>{user.name}</div>
          <div>{user.email}</div>
        </>
      ))}
    </div>
  )
}