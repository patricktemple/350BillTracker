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
import CityBillSponsorList from './CityBillSponsorList';
import StateBillDetails from './StateBillDetails';
import { useHistory } from 'react-router-dom';

interface Props {
  bill: Bill;
}

interface Props {
  match: { params: { billId: number } };
}

interface FormData {
  notes: string;
  nickname: string;
  twitterSearchTerms: string[];
}

/* 
1. Rewrite this to use CSS grid instead of bootstrap grid
2. Factor out all the common parts, and put the city-specific parts into a city component

*/
export default function BillDetailsPage(props: Props): ReactElement {
  const billId = props.match.params.billId;

  const [bill, setBill] = useState<Bill | null>(null);

  const history = useHistory();

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/saved-bills/' + billId,
    {
      notes: '',
      nickname: '',
      twitterSearchTerms: []
    }
  );

  const [twitterSearchTermsRaw, setTwitterSearchTermsRaw] =
    useState<string>('');

  const [attachments, setAttachments] = useState<BillAttachment[] | null>(null);

  const [powerHours, setPowerHours] = useState<PowerHour[] | null>(null);

  const [showDeleteBillConfirmation, setShowDeleteBillConfirmation] =
    useState<boolean>(false);

  const [addAttachmentModalOpen, setAddAttachmentModalOpen] =
    useState<boolean>(false);

  const [createPowerHourModalOpen, setCreatePowerHourModalOpen] =
    useState<boolean>(false);

  const apiFetch = useApiFetch();

  function loadAttachments() {
    apiFetch(`/api/saved-bills/${billId}/attachments`).then((response) => {
      setAttachments(response);
    });
  }

  function loadPowerHours() {
    apiFetch(`/api/saved-bills/${billId}/power-hours`).then((response) => {
      setPowerHours(response);
    });
  }

  useMountEffect(() => {
    apiFetch(`/api/saved-bills/${billId}`).then((response) => {
      setBill(response);
      setFormData({
        notes: response.notes,
        nickname: response.nickname,
        twitterSearchTerms: response.twitterSearchTerms
      });
      setTwitterSearchTermsRaw(response.twitterSearchTerms.join(','));
    });
  });

  useMountEffect(() => {
    loadAttachments();
    loadPowerHours();
  });

  function handleNotesChanged(event: any) {
    setFormData({ ...formData, notes: event.target.value });
  }

  // TODO: Get real types for all my Events
  function handleNicknameChanged(event: any) {
    setFormData({ ...formData, nickname: event.target.value });
  }

  function handleTwitterSearchTermsChanged(event: any) {
    setTwitterSearchTermsRaw(event.target.value);
    const twitterSearchTermsList = event.target.value
      .split(',')
      .map((term: string) => term.trim())
      .filter(Boolean);
    setFormData({ ...formData, twitterSearchTerms: twitterSearchTermsList });
  }

  function handleAddAttachmentClicked() {
    setAddAttachmentModalOpen(true);
  }

  function handleAddAttachment(description: string, url: string) {
    setAddAttachmentModalOpen(false);
    apiFetch(`/api/saved-bills/${billId}/attachments`, {
      method: 'POST',
      body: { url, name: description }
    }).then((response) => {
      loadAttachments();
    });
  }

  function handleDeleteAttachment(event: any, id: number) {
    event.preventDefault();
    apiFetch(`/api/saved-bills/-/attachments/` + id, {
      method: 'DELETE'
    }).then((response) => {
      loadAttachments();
    });
  }

  function handleRemoveBill(event: any) {
    event.preventDefault();
    setShowDeleteBillConfirmation(true);
  }

  function handleConfirmRemoveBill() {
    setShowDeleteBillConfirmation(false);
    apiFetch(`/api/saved-bills/` + billId, {
      method: 'DELETE'
    }).then((response) => {
      history.replace('/bills');
    });
  }

  function handlePowerHourCreated() {
    loadPowerHours();
  }

  const powerHourHelpRef = useRef<HTMLSpanElement>(null);
  const [powerHourHelpVisible, setPowerHourHelpVisible] =
    useState<boolean>(false);

  const twitterSearchHelpRef = useRef<HTMLSpanElement>(null);
  const [twitterSearchHelpVisible, setTwitterSearchHelpVisible] =
    useState<boolean>(false);

  if (!bill) {
    return <div>Loading</div>; // TODO improve
  }

  return (
    <div>
      <div className={styles.title}>{formData.nickname || bill.name}</div>
      <Form onSubmit={(e) => e.preventDefault()} className={styles.page}>
        <>
          <div className={styles.label}>Bill number</div>
          <div className={styles.content}>{bill.codeName}</div>
          <div className={styles.label}>Official title</div>

          <div className={styles.content}>{bill.name}</div>

          <div className={styles.label}>Official description</div>
          <div className={styles.content}>{bill.description}</div>
          <div className={styles.label}>Status</div>
          <div className={styles.content}>{bill.status}</div>
          <div className={styles.label}>Our nickname</div>
          <div className={styles.content}>
            <Form.Control
              type="text"
              size="sm"
              placeholder='e.g. "Skip the stuff"'
              value={formData.nickname}
              onChange={handleNicknameChanged}
            />
          </div>
          <div className={styles.label}>
            <div style={{ fontWeight: 'bold' }}>
              Attachments {attachments != null && <>({attachments.length})</>}:
            </div>
            <Button
              size="sm"
              variant="outline-secondary"
              onClick={handleAddAttachmentClicked}
              className="mt-2 mb-2 d-block"
            >
              Attach a link
            </Button>
            <AddAttachmentModal
              show={addAttachmentModalOpen}
              handleAddAttachment={handleAddAttachment}
              onHide={() => setAddAttachmentModalOpen(false)}
            />
          </div>
          <div className={styles.content}>
            {attachments == null ? (
              'Loading...'
            ) : (
              <>
                {attachments.map((a) => (
                  <div key={a.id}>
                    <a href={a.url} target="attachment">
                      {a.name}
                    </a>
                    &nbsp;
                    <a
                      href="#"
                      onClick={(e) => handleDeleteAttachment(e, a.id)}
                    >
                      [Remove]
                    </a>
                  </div>
                ))}
              </>
            )}
          </div>
          <div className={styles.label}>
            <div>
              <div style={{ fontWeight: 'bold' }}>
                Power hours{' '}
                <span
                  onClick={() => setPowerHourHelpVisible(!powerHourHelpVisible)}
                  ref={powerHourHelpRef}
                  style={{ cursor: 'pointer' }}
                >
                  <MdHelpOutline />
                </span>
              </div>
              <Overlay
                target={powerHourHelpRef.current}
                placement="right"
                show={powerHourHelpVisible}
              >
                <Popover style={{ width: '500px', maxWidth: '500px' }}>
                  <Popover.Header as="h3">Power hours</Popover.Header>
                  <Popover.Body>
                    <p>
                      You can generate a Google Sheet for a Power Hour on this
                      bill with the latest sponsorships and contact info.
                    </p>
                    <p className="mb-0">
                      These sheets are designed for Power Hours involving calls
                      to a bunch of legislators pushing them to sponsor the
                      bill. For other kinds of Power Hour, such as calls to the
                      governor or calls not related to a specific bill, this may
                      not be useful.
                    </p>
                  </Popover.Body>
                </Popover>
              </Overlay>
              {powerHours != null && (
                <>
                  <Button
                    size="sm"
                    variant="outline-secondary"
                    onClick={() => setCreatePowerHourModalOpen(true)}
                    className="mb-2 d-block"
                  >
                    Create power hour
                  </Button>
                  <CreatePowerHourModal
                    bill={bill}
                    oldPowerHours={powerHours}
                    show={createPowerHourModalOpen}
                    handlePowerHourCreated={handlePowerHourCreated}
                    onHide={() => setCreatePowerHourModalOpen(false)}
                  />
                </>
              )}
            </div>
          </div>
          <div className={styles.content}>
            {powerHours == null ? (
              'Loading...'
            ) : (
              <>
                {powerHours.map((p, i) => (
                  <div key={p.id}>
                    <a href={p.spreadsheetUrl} target="_blank" rel="noreferrer">
                      {p.title}
                    </a>
                    {i == powerHours.length - 1 && ' (latest)'}
                  </div>
                ))}
              </>
            )}
          </div>
          <div className={styles.label}>
            Twitter search terms{' '}
            <span
              onClick={() =>
                setTwitterSearchHelpVisible(!twitterSearchHelpVisible)
              }
              ref={twitterSearchHelpRef}
              style={{ cursor: 'pointer' }}
            >
              <MdHelpOutline />
            </span>
            <Overlay
              target={twitterSearchHelpRef.current}
              placement="right"
              show={twitterSearchHelpVisible}
            >
              <Popover style={{ width: '500px', maxWidth: '500px' }}>
                <Popover.Header as="h3">Twitter search keywords</Popover.Header>
                <Popover.Body>
                  <p>
                    It&apos;s often helpful to search council members&apos;
                    Twitter accounts for keywords related to a bill, while
                    researching their stance on the bill.
                  </p>
                  <p className="mb-0">
                    You can keywords for the bill here, comma-separated. Then
                    all the <TwitterIcon style={{ width: '1rem' }} /> icons
                    above, next to the council members, will link to a search of
                    that council member&apos;s Twitter history for those terms.
                    (In the Power Hour spreadsheets, the{' '}
                    <em>Relevant tweets</em> links do these same searches.)
                  </p>
                </Popover.Body>
              </Popover>
            </Overlay>
          </div>
          <div className={styles.content}>
            <Form.Control
              type="text"
              size="sm"
              placeholder="Enter comma-separated terms, e.g. solar, climate, fossil fuels"
              value={twitterSearchTermsRaw}
              onChange={handleTwitterSearchTermsChanged}
            />
          </div>
          <div className={styles.label}>Our notes</div>
          <div className={styles.content}>
            <Form.Control
              as="textarea"
              rows={3}
              size="sm"
              value={formData.notes}
              placeholder="Add our notes about this bill"
              onChange={handleNotesChanged}
            />
          </div>
          {bill.type === 'CITY' ? (
            <CityBillSponsorList
              bill={bill}
              twitterSearchTerms={formData.twitterSearchTerms}
            />
          ) : (
            <div className={styles.fullWidth}>
              <StateBillDetails bill={bill} />
            </div>
          )}
          <div className={styles.label}>
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleRemoveBill}
              className="mt-2 mb-2"
            >
              Remove bill from tracker
            </Button>
            <ConfirmDeleteBillModel
              show={showDeleteBillConfirmation}
              handleConfirm={handleConfirmRemoveBill}
              handleCloseWithoutConfirm={() =>
                setShowDeleteBillConfirmation(false)
              }
            />
            <div style={{ fontStyle: 'italic' }}>{saveStatus}</div>
          </div>
        </>
      </Form>
    </div>
  );
}
