import React, { ReactElement, useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Bill, SponsorList, BillAttachment, PowerHour } from './types';
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

  const [sponsorships, setSponsorships] = useState<SponsorList | null>(
    null
  );

  useMountEffect(() => {
    apiFetch(`/api/city-bills/${bill.id}/sponsorships`).then((response) => {
      setSponsorships(response);
    });
  });

  return (
    <>
      <div className={styles.label}>
        Lead sponsor
      </div>
      <div className={styles.content}>
        {sponsorships == null ? ("Loading...") : sponsorships.leadSponsor && <BillSponsorItem person={sponsorships.leadSponsor} twitterSearchTerms={twitterSearchTerms} />}
      </div>
      <div className={styles.label}>
        <div>
          Co-sponsors{' '}
          {sponsorships != null && <>({sponsorships.cosponsors.length})</>}:
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
