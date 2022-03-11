import React, { useState } from 'react';
import {
  Person,
  SingleMemberSponsorship,
  OfficeContact,
  CouncilMemberCommitteeMembership
} from '../types';
import useMountEffect from '@restart/hooks/useMountEffect';
import { Link } from 'react-router-dom';
import useApiFetch from '../useApiFetch';
import styles from '../style/components/PersonDetailsPanel.module.scss';
import { DetailLabel, DetailContent } from '../components/DetailTable';

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
      <DetailLabel>Name</DetailLabel>
      <DetailContent>{person.name}</DetailContent>
      <DetailLabel>Title</DetailLabel>
      <DetailContent>{person.title}</DetailContent>
      <DetailLabel>Borough</DetailLabel>
      <DetailContent>{person.councilMember!.borough}</DetailContent>
      <DetailLabel>Email</DetailLabel>
      <DetailContent>{person.email}</DetailContent>
      <DetailLabel>District phone</DetailLabel>
      <DetailContent>{districtPhoneText}</DetailContent>
      <DetailLabel>Legislative phone</DetailLabel>
      <DetailContent>{legislativePhoneText}</DetailContent>
      <DetailLabel>Party</DetailLabel>
      <DetailContent>{person.party}</DetailContent>
      <DetailLabel>Committees</DetailLabel>
      <DetailContent>
        {committeeMemberships == null
          ? 'Loading...'
          : committeeMemberships.map((membership) => (
              <div key={membership.committee.id}>
                {membership.committee.name}
                {membership.isChair && ' (chair)'}
              </div>
            ))}
      </DetailContent>
      <DetailLabel>Website</DetailLabel>
      <DetailContent>
        {person.councilMember!.website && (
          <a href={person.councilMember!.website} target="website">
            Visit website
          </a>
        )}
      </DetailContent>
      <DetailLabel>Twitter</DetailLabel>
      <DetailContent>
        {person.twitter && (
          <a href={`https://twitter.com/${person.twitter}`} target="twitter">
            @{person.twitter}
          </a>
        )}
      </DetailContent>
      <DetailLabel>
        <div style={{ fontWeight: 'bold' }}>Sponsored bills</div>
      </DetailLabel>
      <DetailContent>
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
      </DetailContent>
    </>
  );
}
