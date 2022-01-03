import React from 'react';
import { CitySponsorship } from './types';
import { Link } from 'react-router-dom';
import Stack from 'react-bootstrap/Stack';

import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface Props {
  sponsorships: CitySponsorship[];
  twitterSearchTerms: string[];
}

function getTwitterSearchUrl(searchTerms: string[], twitterHandle: string) {
  return '';
  // TODO: fix this

  // Need to keep this in sync with the backend implementation
  // const queryTerms = searchTerms
  //   .map((term: string) => `"${term}"`)
  //   .join(' OR ');
  // const fullQuery = `(from:${twitterHandle}) ${queryTerms}`;
  // return (
  //   'https://twitter.com/search?' +
  //   new URLSearchParams({ q: fullQuery }).toString()
  // );
}

export default function BillSponsorList(props: Props) {
  return (
    <Stack direction="vertical">
      {props.sponsorships.map((s) => (
        <div key={s.person.id}>
          <Link to={'/people/' + s.person.id}>{s.person.name}</Link>
          {s.sponsorSequence == 0 && ' (lead)'}{' '}
          {s.person.twitter && (
            <span style={{ marginLeft: '0.5rem' }}>
              <a
                href={getTwitterSearchUrl(
                  props.twitterSearchTerms,
                  s.person.twitter
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
