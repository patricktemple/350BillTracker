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
    return (
      <Accordion.Item key={chamber} eventKey={chamber}>
        <Accordion.Header>
            <div>
          <div style={{fontWeight: 'bold'}}>{chamber} bill {chamberDetails?.basePrintNo}</div>
          <div>{chamberDetails?.status}
          </div>
          <div>
              {chamberDetails?.sponsorCount} sponsors
          </div></div>
        </Accordion.Header>
        <Accordion.Body>
            Body
        </Accordion.Body>
    </Accordion.Item>
    )
}

interface Props {
    bill: Bill;
}
export default function StateBillDetails({ bill }: Props) {
    return (
        <Accordion>
          <ChamberDetails chamber="Senate" chamberDetails={bill.stateBill!.senateBill} />
          <ChamberDetails chamber="Assembly" chamberDetails={bill.stateBill!.assemblyBill} />
        </Accordion>
    );
}