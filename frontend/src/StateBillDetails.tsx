import React, { useState } from 'react';
import { Bill, StateBillSponsorships, Person } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import useApiFetch from './useApiFetch';
import BillSponsorList from './BillSponsorList';
import { StateChamberBill } from './types';
import Accordion from 'react-bootstrap/Accordion';

import styles from './style/StateBillDetails.module.scss';

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
  return (
    <Accordion.Item key={chamber} eventKey={chamber}>
      <Accordion.Header>
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
            </div>
            <div className={styles.sponsorList}>
              <span style={{ fontWeight: 'bold' }}>
                Sponsors{sponsors != null && <> ({sponsors.length})</>}
              </span>
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
              <span style={{ fontWeight: 'bold' }}>
                Non-sponsors
                {nonSponsors != null && <> ({nonSponsors.length})</>}
              </span>
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
