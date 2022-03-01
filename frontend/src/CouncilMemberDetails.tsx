import React, { useState } from 'react';
import {
  Person,
  SingleMemberSponsorship,
  OfficeContact,
  CouncilMemberCommitteeMembership
} from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import { Link } from 'react-router-dom';
import useApiFetch from './useApiFetch';
import styles from './style/components/PersonDetailsPanel.module.scss';

interface Props {
  person: Person;
}

export default function CouncilMemberDetails(props: Props) {
  const person = props.person;

  const apiFetch = useApiFetch();

  const [contacts, setContacts] = useState<OfficeContact[] | null>(null);
  const [sponsorships, setSponsorships] = useState<
    SingleMemberSponsorship[] | null
  >(null);
  const [committeeMemberships, setCommitteeMemberships] = useState<
    CouncilMemberCommitteeMembership[] | null
  >(null);

  useMountEffect(() => {
    apiFetch(`/api/council-members/${person.id}/sponsorships`).then(
      (response) => {
        setSponsorships(response);
      }
    );
    apiFetch(`/api/persons/${person.id}/contacts`).then((response) => {
      setContacts(response);
    });
    apiFetch(`/api/council-members/${person.id}/committees`).then(
      (response) => {
        setCommitteeMemberships(response);
      }
    );
  });

  const districtPhoneText =
    contacts &&
    contacts
      .filter((c) => c.type === 'DISTRICT_OFFICE' && c.phone)
      .map((c) => c.phone);
  const legislativePhoneText =
    contacts &&
    contacts
      .filter((c) => c.type === 'CENTRAL_OFFICE' && c.phone)
      .map((c) => c.phone);
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
      <div className={styles.content}>{districtPhoneText}</div>
      <div className={styles.label}>Legislative phone</div>
      <div className={styles.content}>{legislativePhoneText}</div>
      <div className={styles.label}>Party</div>
      <div className={styles.content}>{person.party}</div>
      <div className={styles.label}>Committees</div>
      <div className={styles.content}>
        {committeeMemberships == null
          ? 'Loading...'
          : committeeMemberships.map((membership) => (
              <div key={membership.committee.id}>
                {membership.committee.name}
                {membership.isChair && ' (chair)'}
              </div>
            ))}
      </div>
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
              <Link
                className="d-block"
                to={'/bills/' + s.bill.id}
                key={s.bill.id}
              >
                {s.bill.cityBill!.file}: <em>{s.bill.displayName}</em>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
