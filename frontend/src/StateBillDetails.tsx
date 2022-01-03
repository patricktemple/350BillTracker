import React, { ReactElement, useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import {
  Bill,
  CitySponsorship,
  BillAttachment,
  PowerHour,
  StateBillSponsorships,
  Person
} from './types';
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
import { StateChamberBill } from './types';
import LazyAccordionBody from './LazyAccordionBody';
import Accordion from 'react-bootstrap/Accordion';

import styles from './style/StateBillDetails.module.scss';
import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface ChamberProps {
  chamber: string;
  chamberDetails: StateChamberBill | null;
  sponsors?: Person[];
  nonSponsors?: Person[];
  twitterSearchTerms: string[];
}

function ChamberDetails({
  chamber,
  chamberDetails,
  sponsors,
  nonSponsors,
  twitterSearchTerms
}: ChamberProps) {
  // todo handle null chamber details
  // todo explain senate vs assembly website?
  return (
    <Accordion.Item key={chamber} eventKey={chamber}>
      <Accordion.Header>
        <div>
          <div style={{ fontWeight: 'bold' }}>
            {chamber} bill {chamberDetails?.basePrintNo}
          </div>
          <div>{chamberDetails?.status}</div>
          <div>{chamberDetails?.sponsorCount} sponsors</div>
        </div>
      </Accordion.Header>
      <Accordion.Body>
        <div className={styles.chamberDetails}>
          <div className={styles.info}>
            <a
              className="d-block"
              href={chamberDetails?.senateWebsite}
              rel="noreferrer"
              target="_blank"
            >
              View on Senate website
            </a>
            <a
              className="d-block"
              href={chamberDetails?.assemblyWebsite}
              rel="noreferrer"
              target="_blank"
            >
              View on Assembly website
            </a>
          </div>
          <div className={styles.sponsorList}>
            <span style={{fontWeight: 'bold' }}>Sponsors</span>
            {sponsors != null ? (
              <BillSponsorList
                persons={sponsors}
                twitterSearchTerms={twitterSearchTerms}
              />
            ) : (
              'Loading...'
            )}
          </div>
          <div className={styles.nonSponsorList}>
            <span style={{fontWeight: 'bold' }}>Non-sponsors</span>
            {nonSponsors != null ? (
              <BillSponsorList
                persons={nonSponsors}
                twitterSearchTerms={twitterSearchTerms}
              />
            ) : (
              'Loading...'
            )}
          </div>
        </div>
      </Accordion.Body>
    </Accordion.Item>
  );
}

interface Props {
  bill: Bill;
  twitterSearchTerms: string[];
}
export default function StateBillDetails({ bill, twitterSearchTerms }: Props) {
  const apiFetch = useApiFetch();

  const [sponsorships, setSponsorships] =
    useState<StateBillSponsorships | null>(null);

  useMountEffect(() => {
    apiFetch(`/api/state-bills/${bill.id}/sponsorships`).then((response) => {
      setSponsorships(response);
    });
  });

  return (
    <Accordion>
      <ChamberDetails
        chamber="Senate"
        chamberDetails={bill.stateBill!.senateBill}
        sponsors={sponsorships?.senateSponsors}
        nonSponsors={sponsorships?.senateNonSponsors}
        twitterSearchTerms={twitterSearchTerms}
      />
      <ChamberDetails
        chamber="Assembly"
        chamberDetails={bill.stateBill!.assemblyBill}
        sponsors={sponsorships?.assemblySponsors}
        nonSponsors={sponsorships?.assemblyNonSponsors}
        twitterSearchTerms={twitterSearchTerms}
      />
    </Accordion>
  );
}
