import React, { ReactElement, useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Bill, CitySponsorship, BillAttachment, PowerHour } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import AddAttachmentModal from './AddAttachmentModal';
import useAutosavingFormData from './utils/useAutosavingFormData';
import ConfirmDeleteBillModel from './ConfirmDeleteBillModal';
import CreatePowerHourModal from './CreatePowerHourModal';
import useApiFetch from './useApiFetch';
import BillSponsorList from './BillSponsorList';
import Popover from 'react-bootstrap/Popover';
import Overlay from 'react-bootstrap/Overlay';
import { MdHelpOutline } from 'react-icons/md';
import styles from './style/BillDetailsPage.module.scss';

import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface Props {
  bill: Bill;
  twitterSearchTerms: string[];
}

export default function CityBillSponsorList({
  bill,
  twitterSearchTerms
}: Props) {
  const apiFetch = useApiFetch();

  const [sponsorships, setSponsorships] = useState<CitySponsorship[] | null>(
    null
  );

  useMountEffect(() => {
    apiFetch(`/api/city-bills/${bill.id}/sponsorships`).then((response) => {
      setSponsorships(response);
    });
  });

  const positiveSponsors = sponsorships
    ?.filter((s: CitySponsorship) => s.isSponsor)
    .map((s) => s.person);
  const negativeSponsors = sponsorships
    ?.filter((s: CitySponsorship) => !s.isSponsor)
    .map((s) => s.person);

  return (
    <>
      <div className={styles.label}>
        <div>
          Sponsors{' '}
          {positiveSponsors != null && <>({positiveSponsors.length})</>}:
        </div>
        <div style={{ fontSize: '0.8rem', fontStyle: 'italic' }}>
          Note: Due to a Twitter bug, the Twitter search sometimes displays 0
          results even when there should be should be matching tweets.
          Refreshing the Twitter page often fixes this.
        </div>
      </div>
      <div className={styles.sponsorList}>
        {positiveSponsors == null ? (
          'Loading...'
        ) : (
          <BillSponsorList
            persons={positiveSponsors}
            twitterSearchTerms={twitterSearchTerms}
          />
        )}
      </div>
      <div className={styles.nonSponsorLabel}>
        Non-sponsors{' '}
        {negativeSponsors != null && <>({negativeSponsors.length})</>}:
      </div>
      <div className={styles.nonSponsorList}>
        {negativeSponsors == null ? (
          'Loading...'
        ) : (
          <BillSponsorList
            persons={negativeSponsors}
            twitterSearchTerms={twitterSearchTerms}
          />
        )}
      </div>
    </>
  );
}
