import React, { useState } from 'react';
import { Person, OfficeContact } from '../types';
import styles from '../style/components/PersonDetailsPanel.module.scss';
import useApiFetch from '../useApiFetch';
import useMountEffect from '@restart/hooks/esm/useMountEffect';

interface Props {
  person: Person;
}

export default function StafferDetails(props: Props) {
  const person = props.person;

  const [contacts, setContacts] = useState<OfficeContact[] | null>(null);

  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch(`/api/persons/${person.id}/contacts`).then((response) => {
      setContacts(response);
    });
  });

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
      <div className={styles.content}>
        {contacts &&
          contacts
            .map((c) => c.phone)
            .filter(Boolean)
            .join(', ')}
      </div>
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
