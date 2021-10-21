import React from 'react';
import { BillSponsorship } from './types';
import { Link } from 'react-router-dom';
import Stack from 'react-bootstrap/Stack';

import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface Props {
  sponsorships: BillSponsorship[];
  twitterSearchTerms: string[];
}

function getTwitterSearchUrl(searchTerms: string[], twitterHandle: string) {
  // Need to keep this in sync with the backend implementation
  const queryTerms = searchTerms.map((term: string) => `"${term}"`).join(" OR ");
  const fullQuery = `(from:${twitterHandle}) ${queryTerms}`;
  return "https://twitter.com/search?" + new URLSearchParams({q: fullQuery}).toString();
}

export default function BillSponsorList(props: Props) {
  return (<Stack direction="vertical">
  {props.sponsorships.map((s) => (
    <div key={s.legislator.id}>
      <Link to={'/council-members/' + s.legislator.id}>
        {s.legislator.name}
      </Link>{' '}
      {s.legislator.twitter && (<span style={{ marginLeft: '0.5rem' }}>
        <a
          href={getTwitterSearchUrl(props.twitterSearchTerms, s.legislator.twitter)}
          target="_blank"
          rel="noreferrer"
        >
          <TwitterIcon style={{width: '1rem'}}/>
        </a>
      </span>)}
    </div>
  ))}
</Stack>);
}
