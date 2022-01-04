import React from 'react';
import { Person } from './types';
import { Link } from 'react-router-dom';
import Stack from 'react-bootstrap/Stack';

import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface Props {
  persons: Person[];
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

export default function BillSponsorList(props: Props) {
  // TODO: Fix handling of lead sponsor
  return (
    <Stack direction="vertical">
      {props.persons.map((person) => (
        <div key={person.id}>
          <Link to={'/people/' + person.id}>{person.name}</Link>
          {/* {s.sponsorSequence == 0 && ' (lead)'}{' '} */}
          {person.twitter && (
            <span style={{ marginLeft: '0.5rem' }}>
              <a
                href={getTwitterSearchUrl(
                  props.twitterSearchTerms,
                  person.twitter
                )}
                target="_blank"
                rel="noreferrer"
              >
                <TwitterIcon style={{ width: '1rem' }} />
              </a>
            </span>
          )}
        </div>
      ))}
    </Stack>
  );
}
