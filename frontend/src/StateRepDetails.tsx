
import { Person  } from './types';
import React from 'react';
import styles from './style/PersonDetailsPanel.module.scss';

interface Props {
  person: Person;
}

export default function StateRepDetails(props: Props) {
  const person = props.person;

  // TODO: Display their sponsorships here, too (can do in later PR from State impl)
  return (
      <>
      <div className={styles.label}>Name</div>
      <div className={styles.content}>{person.name}</div>
      <div className={styles.label}>Title</div>
      <div className={styles.content}>{person.title}</div>
      <div className={styles.label}>Email</div>
      <div className={styles.content}>{person.email}</div>
      <div className={styles.label}>Phone</div>
      <div className={styles.content}>{person.phone}</div>
      <div className={styles.label}>Party</div>
      <div className={styles.content}>{person.party}</div>
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
