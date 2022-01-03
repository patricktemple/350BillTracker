import React, { useState, ReactElement } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { Person, SingleMemberSponsorship, Staffer, Uuid } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Stack from 'react-bootstrap/Stack';
import { Link } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import useAutosavingFormData from './utils/useAutosavingFormData';
import useApiFetch from './useApiFetch';
import Button from 'react-bootstrap/Button';
import AddStafferModal from './AddStafferModal';
import styles from './style/PersonDetailsPanel.module.scss';
import { MdDriveEta } from 'react-icons/md';

interface Props {
  person: Person;
}

export default function CouncilMemberDetails(props: Props) {
  const person = props.person;

  const apiFetch = useApiFetch();

  const [sponsorships, setSponsorships] = useState<
  SingleMemberSponsorship[] | null
>(null);

  useMountEffect(() => {
    apiFetch(`/api/council-members/${person.id}/sponsorships`).then(
      (response) => {
        setSponsorships(response);
      }
    );
  });


  return (
      <>
      <div className={styles.label}>Name</div>
      <div className={styles.content}>{person.name}</div>
      <div className={styles.label}>Title</div>
      <div className={styles.content}>{person.title}</div>
      <div className={styles.label}>Borough</div>
      <div className={styles.content}>{person.councilMember!.borough}</div>
      <div className={styles.label}>Email</div>
      <div className={styles.content}>{person.email}</div>
      <div className={styles.label}>District phone</div>
      <div className={styles.content}>{person.phone}</div>
      <div className={styles.label}>Legislative phone</div>
      <div className={styles.content}>
        {person.councilMember!.legislativePhone}
      </div>
      <div className={styles.label}>Party</div>
      <div className={styles.content}>{person.party}</div>
      <div className={styles.label}>Website</div>
      <div className={styles.content}>
        {person.councilMember!.website && (
          <a href={person.councilMember!.website} target="website">
            Visit website
          </a>
        )}
      </div>
      <div className={styles.label}>Twitter</div>
      <div className={styles.content}>
        {person.twitter && (
          <a href={`https://twitter.com/${person.twitter}`} target="twitter">
            @{person.twitter}
          </a>
        )}
      </div>
      <div className={styles.label}>
        <div style={{ fontWeight: 'bold' }}>Sponsored bills</div>
      </div>
      <div className={styles.content}>
        {sponsorships == null ? (
          'Loading...'
        ) : (
          <div>
            {sponsorships.map((s) => (
              <Link className="d-block" to={'/bills/' + s.bill.id} key={s.bill.id}>
                {s.bill.cityBill!.file}:{' '}
                <em>{s.bill.nickname || s.bill.name}</em>
              </Link>
            ))}
          </div>
        )}
      </div>
      </>
  );
}
