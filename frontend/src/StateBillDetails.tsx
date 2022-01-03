import React, { ReactElement, useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import {
  Bill,
  CitySponsorship,
  BillAttachment,
  PowerHour,
  StateBillSponsorships
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
import styles from './style/BillDetailsPage.module.scss';
import { StateChamberBill } from './types';
import LazyAccordionBody from './LazyAccordionBody';
import Accordion from 'react-bootstrap/Accordion';

import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface ChamberProps {
  chamber: string;
  chamberDetails: StateChamberBill | null;
}

function ChamberDetails({ chamber, chamberDetails }: ChamberProps) {
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
        <a
          className="d-block"
          href={chamberDetails?.senateWebsite}
          rel="noreferrer"
          target="_blank"
        >
          Senate website
        </a>
        <a
          className="d-block"
          href={chamberDetails?.assemblyWebsite}
          rel="noreferrer"
          target="_blank"
        >
          Assembly website
        </a>
      </Accordion.Body>
    </Accordion.Item>
  );
}

interface Props {
  bill: Bill;
}
export default function StateBillDetails({ bill }: Props) {
  const apiFetch = useApiFetch();

  const [sponsorships, setSponsorships] =
    useState<StateBillSponsorships | null>(null);

  useMountEffect(() => {
    apiFetch(`/api/state-bills/${bill.id}/sponsorships`).then((response) => {
      console.log(response);
      setSponsorships(response);
    });
  });

  return (
    <Accordion>
      <ChamberDetails
        chamber="Senate"
        chamberDetails={bill.stateBill!.senateBill}
      />
      <ChamberDetails
        chamber="Assembly"
        chamberDetails={bill.stateBill!.assemblyBill}
      />
    </Accordion>
  );
}
