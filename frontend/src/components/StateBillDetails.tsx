import React, { useState } from 'react';
import { Bill, StateBillSponsorships, Person, SponsorList } from '../types';
import useMountEffect from '@restart/hooks/useMountEffect';
import useApiFetch from '../useApiFetch';
import BillSponsorList from './BillSponsorList';
import { StateChamberBill } from '../types';
import Accordion from 'react-bootstrap/Accordion';
import BillSponsorItem from './BillSponsorItem';

import styles from '../style/components/StateBillDetails.module.scss';

interface ChamberProps {
  chamber: string;
  chamberDetails: StateChamberBill | null;
  sponsorships?: SponsorList;
  twitterSearchTerms: string[];
}

function ChamberDetails({
  chamber,
  chamberDetails,
  sponsorships,
  twitterSearchTerms
}: ChamberProps) {
  return (
    <Accordion.Item key={chamber} eventKey={chamber}>
      <Accordion.Header className={styles.accordionItem}>
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
            {chamber} bill {chamberDetails?.basePrintNo}
          </div>
          {chamberDetails == null ? (
            <div>Not yet introduced in {chamber}</div>
          ) : (
            <>
              <div>{chamberDetails?.status}</div>
              <div>{chamberDetails?.sponsorCount} sponsors</div>
            </>
          )}
        </div>
      </Accordion.Header>
      {chamberDetails && (
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
              <div className="mt-2">
                <span style={{ fontWeight: 'bold' }}>Lead sponsor: </span>
                {sponsorships?.leadSponsor && (
                  <BillSponsorItem
                    person={sponsorships.leadSponsor}
                    twitterSearchTerms={twitterSearchTerms}
                  />
                )}
              </div>
            </div>
            <div className={styles.sponsorList}>
              <span style={{ fontWeight: 'bold' }}>
                Co-sponsors
                {sponsorships != null && (
                  <> ({sponsorships.cosponsors.length})</>
                )}
              </span>
              {sponsorships != null ? (
                <BillSponsorList
                  persons={sponsorships.cosponsors}
                  twitterSearchTerms={twitterSearchTerms}
                />
              ) : (
                'Loading...'
              )}
            </div>
            <div className={styles.nonSponsorList}>
              <span style={{ fontWeight: 'bold' }}>
                Non-sponsors
                {sponsorships != null && (
                  <> ({sponsorships.nonSponsors.length})</>
                )}
              </span>
              {sponsorships != null ? (
                <BillSponsorList
                  persons={sponsorships.nonSponsors}
                  twitterSearchTerms={twitterSearchTerms}
                />
              ) : (
                'Loading...'
              )}
            </div>
          </div>
        </Accordion.Body>
      )}
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
        sponsorships={sponsorships?.senateSponsorships}
        twitterSearchTerms={twitterSearchTerms}
      />
      <ChamberDetails
        chamber="Assembly"
        chamberDetails={bill.stateBill!.assemblyBill}
        sponsorships={sponsorships?.assemblySponsorships}
        twitterSearchTerms={twitterSearchTerms}
      />
    </Accordion>
  );
}
