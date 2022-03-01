import React, { useState } from 'react';
import { Bill, SponsorList, BillAttachment, PowerHour } from '../types';
import useMountEffect from '@restart/hooks/useMountEffect';
import useApiFetch from '../useApiFetch';
import BillSponsorList from './BillSponsorList';
import styles from '../style/pages/BillDetailsPage.module.scss';

import BillSponsorItem from './BillSponsorItem';

interface Props {
  bill: Bill;
  twitterSearchTerms: string[];
}

export default function CityBillSponsorList({
  bill,
  twitterSearchTerms
}: Props) {
  const apiFetch = useApiFetch();

  const [sponsorships, setSponsorships] = useState<SponsorList | null>(null);

  useMountEffect(() => {
    apiFetch(`/api/city-bills/${bill.id}/sponsorships`).then((response) => {
      setSponsorships(response);
    });
  });

  return (
    <>
      <div className={styles.label}>Lead sponsor</div>
      <div className={styles.content}>
        {sponsorships == null
          ? 'Loading...'
          : sponsorships.leadSponsor && (
              <BillSponsorItem
                person={sponsorships.leadSponsor}
                twitterSearchTerms={twitterSearchTerms}
              />
            )}
      </div>
      <div className={styles.label}>
        <div>
          Co-sponsors{' '}
          {sponsorships != null && <>({sponsorships.cosponsors.length})</>}
        </div>
      </div>
      <div className={styles.sponsorList}>
        {sponsorships == null ? (
          'Loading...'
        ) : (
          <BillSponsorList
            persons={sponsorships.cosponsors}
            twitterSearchTerms={twitterSearchTerms}
          />
        )}
      </div>
      <div className={styles.nonSponsorLabel}>
        Non-sponsors{' '}
        {sponsorships != null && <>({sponsorships.nonSponsors.length})</>}:
      </div>
      <div className={styles.nonSponsorList}>
        {sponsorships == null ? (
          'Loading...'
        ) : (
          <BillSponsorList
            persons={sponsorships.nonSponsors}
            twitterSearchTerms={twitterSearchTerms}
          />
        )}
      </div>
    </>
  );
}
