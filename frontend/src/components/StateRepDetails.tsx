import {
  Person,
  StateRepresentative,
  OfficeContact,
  StateRepresentativeSponsorship
} from '../types';
import React, { useState } from 'react';
import styles from '../style/components/PersonDetailsPanel.module.scss';
import useMountEffect from '@restart/hooks/esm/useMountEffect';
import useApiFetch from '../useApiFetch';
import { Link } from 'react-router-dom';
import { DetailLabel, DetailContent } from '../components/DetailTable';

interface Props {
  person: Person;
  representativeDetails: StateRepresentative;
}

function ContactPanel({ contact }: { contact: OfficeContact }) {
  return (
    <div className="mb-2">
      {contact.city && (
        <div style={{ fontWeight: 'bold' }}>{contact.city} office</div>
      )}
      {contact.phone && <div>Phone: {contact.phone}</div>}
      {contact.fax && <div>Fax: {contact.fax}</div>}
    </div>
  );
}

export default function StateRepDetails(props: Props) {
  const person = props.person;

  const website = props.representativeDetails.website;

  const [contacts, setContacts] = useState<OfficeContact[] | null>(null);

  const [sponsorships, setSponsorships] = useState<
    StateRepresentativeSponsorship[] | null
  >(null);

  const apiFetch = useApiFetch();

  useMountEffect(() => {
    apiFetch(`/api/persons/${person.id}/contacts`).then((response) => {
      setContacts(response);
    });
    const sponsorshipPath =
      person.type === 'SENATOR' ? 'senators' : 'assembly-members';
    apiFetch(`/api/${sponsorshipPath}/${person.id}/sponsorships`).then(
      (response) => {
        setSponsorships(response);
      }
    );
  });

  // TODO: Display their sponsorships here, too (can do in later PR from State impl)
  return (
    <>
      <DetailLabel>Name</DetailLabel>
      <DetailContent>{person.name}</DetailContent>
      <DetailLabel>Title</DetailLabel>
      <DetailContent>{person.title}</DetailContent>
      <DetailLabel>Email</DetailLabel>
      <DetailContent>{person.email}</DetailContent>
      {/* TODO add back styles.contactInfo for all caps */}
      <DetailLabel>Contact info</DetailLabel>
      <DetailContent>
        {contacts &&
          contacts.map((contact, index) => (
            <ContactPanel contact={contact} key={index} />
          ))}
      </DetailContent>
      <DetailLabel>Party</DetailLabel>
      <DetailContent>{person.party}</DetailContent>
      <DetailLabel>District website</DetailLabel>
      <DetailContent>
        {website && (
          <a href={website} target="_blank" rel="noreferrer">
            District {props.representativeDetails.district}
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
                <em>{s.bill.displayName}</em>
              </Link>
            ))}
          </div>
        )}
      </DetailContent>
    </>
  );
}
