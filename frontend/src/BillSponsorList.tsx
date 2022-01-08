import React from 'react';
import { Person } from './types';
import Stack from 'react-bootstrap/Stack';
import BillSponsorItem from './BillSponsorItem';


interface Props {
  persons: Person[];
  twitterSearchTerms: string[];
}

export default function BillSponsorList(props: Props) {
  return (
    <Stack direction="vertical">
      {props.persons.map((person) => (
        <BillSponsorItem key={person.id} person={person} twitterSearchTerms={props.twitterSearchTerms} />
      ))}
    </Stack>
  );
}
