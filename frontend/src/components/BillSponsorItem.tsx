import React from 'react';
import { Person } from '../types';
import { Link } from 'react-router-dom';

import { ReactComponent as TwitterIcon } from '../assets/twitter.svg';

interface Props {
  person: Person;
  twitterSearchTerms: string[];
}

function getTwitterSearchUrl(searchTerms: string[], twitterHandle: string) {
  // Need to keep this in sync with the backend implementation
  const queryTerms = searchTerms
    .map((term: string) => `"${term}"`)
    .join(' OR ');
  const fullQuery = `(from:${twitterHandle}) ${queryTerms}`;
  return (
    'https://twitter.com/search?' +
    new URLSearchParams({ q: fullQuery }).toString()
  );
}

export default function BillSponsorItem({ person, twitterSearchTerms }: Props) {
  return (
    <span>
      <Link to={'/people/' + person.id}>{person.name}</Link>
      {person.twitter && (
        <span style={{ marginLeft: '0.5rem' }}>
          <a
            href={getTwitterSearchUrl(twitterSearchTerms, person.twitter)}
            target="_blank"
            rel="noreferrer"
          >
            <TwitterIcon style={{ width: '1rem' }} />
          </a>
        </span>
      )}
    </span>
  );
}
