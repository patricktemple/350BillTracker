import React from 'react';
import { Person  } from './types';
import styles from './style/PersonDetailsPanel.module.scss';

interface Props {
  person: Person;
}

export default function StafferDetails(props: Props) {
  const person = props.person;

  return (
      <>
      <div className={styles.label}>Name</div>
      <div className={styles.content}>{person.name}</div>
      <div className={styles.label}>Title</div>
      <div className={styles.content}>{person.title}</div>
      {/* <div className={styles.label}>Works for</div>
      <div className={styles.content}>{person.staffer!.}</div> */}
      <div className={styles.label}>Email</div>
      <div className={styles.content}>{person.email}</div>
      <div className={styles.label}>Phone</div>
      <div className={styles.content}>{person.phone}</div>
      <div className={styles.label}>Twitter</div>
      <div className={styles.content}>
        {person.twitter && (
          <a href={`https://twitter.com/${person.twitter}`} target="twitter">
            @{person.twitter}
          </a>
        )}
      </div>
      </>
  );
}
