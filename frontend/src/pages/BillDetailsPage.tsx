import React, { ReactElement, useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Bill, BillAttachment, PowerHour } from '../types';
import useMountEffect from '@restart/hooks/useMountEffect';
import AddAttachmentModal from '../components/AddAttachmentModal';
import useAutosavingFormData from '../utils/useAutosavingFormData';
import ConfirmDeleteBillModel from '../components/ConfirmDeleteBillModal';
import CreatePowerHourModal from '../components/CreatePowerHourModal';
import useApiFetch from '../useApiFetch';
import Popover from 'react-bootstrap/Popover';
import Overlay from 'react-bootstrap/Overlay';
import { MdHelpOutline } from 'react-icons/md';
import styles from '../style/pages/BillDetailsPage.module.scss';
import PageHeader from '../components/PageHeader';
import { ReactComponent as TrashIcon } from '../assets/trash.svg';

import { ReactComponent as TwitterIcon } from '../assets/twitter.svg';
import CityBillSponsorList from '../components/CityBillDetails';
import StateBillDetails from '../components/StateBillDetails';
import { useHistory } from 'react-router-dom';
import DetailTable, {
  DetailLabel,
  DetailContent
} from '../components/DetailTable';

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

export default function BillDetailsPage(props: Props): ReactElement {
  const billId = props.match.params.billId;

  const [bill, setBill] = useState<Bill | null>(null);

  const history = useHistory();

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/bills/' + billId,
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
    apiFetch(`/api/bills/${billId}/attachments`).then((response) => {
      setAttachments(response);
    });
  }

  function loadPowerHours() {
    apiFetch(`/api/bills/${billId}/power-hours`).then((response) => {
      setPowerHours(response);
    });
  }

  useMountEffect(() => {
    apiFetch(`/api/bills/${billId}`).then((response) => {
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
    apiFetch(`/api/bills/${billId}/attachments`, {
      method: 'POST',
      body: { url, name: description }
    }).then((response) => {
      loadAttachments();
    });
  }

  function handleDeleteAttachment(event: any, id: number) {
    event.preventDefault();
    apiFetch(`/api/bills/-/attachments/` + id, {
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
    apiFetch(`/api/bills/` + billId, {
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
    return <div>Loading</div>;
  }

  return (
    <div>
      <PageHeader>{formData.nickname || bill.name}</PageHeader>
      <Form onSubmit={(e) => e.preventDefault()} className={styles.page}>
        <DetailTable>
          <DetailLabel>Bill number</DetailLabel>
          <DetailContent>{bill.codeName}</DetailContent>
          <DetailLabel>Official title</DetailLabel>

          <DetailContent>{bill.name}</DetailContent>

          <DetailLabel>Official description</DetailLabel>
          <DetailContent>{bill.description}</DetailContent>
          <DetailLabel>Status</DetailLabel>
          <DetailContent>{bill.status}</DetailContent>
          <DetailLabel>Our nickname</DetailLabel>
          <DetailContent>
            <Form.Control
              type="text"
              placeholder='e.g. "Skip the stuff"'
              value={formData.nickname}
              onChange={handleNicknameChanged}
            />
          </DetailContent>
          <DetailLabel>
            <div style={{ fontWeight: 'bold' }}>
              Attachments {attachments != null && <>({attachments.length})</>}
            </div>
          </DetailLabel>
          <DetailContent>
            {attachments == null ? (
              'Loading...'
            ) : (
              <>
                {attachments?.length > 0 && (
                  <div className="mb-2">
                    {attachments.map((a) => (
                      <div key={a.id}>
                        <a href={a.url} target="attachment">
                          {a.name}
                        </a>
                        &nbsp;
                        <TrashIcon
                          onClick={(e) => handleDeleteAttachment(e, a.id)}
                          className={styles.trashIcon}
                        />
                      </div>
                    ))}
                  </div>
                )}
                <Button
                  size="sm"
                  variant="outline-secondary"
                  onClick={handleAddAttachmentClicked}
                  className="mb-2 d-block"
                >
                  Attach a link
                </Button>
                <AddAttachmentModal
                  show={addAttachmentModalOpen}
                  handleAddAttachment={handleAddAttachment}
                  onHide={() => setAddAttachmentModalOpen(false)}
                />
              </>
            )}
          </DetailContent>
          {bill.type === 'CITY' && (
            <>
              <DetailLabel>
                <div>
                  <div style={{ fontWeight: 'bold' }}>
                    Power hours{' '}
                    <span
                      onClick={() =>
                        setPowerHourHelpVisible(!powerHourHelpVisible)
                      }
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
                          You can generate a Google Sheet for a Power Hour on
                          this bill with the latest sponsorships and contact
                          info.
                        </p>
                        <p className="mb-0">
                          These sheets are designed for Power Hours involving
                          calls to a bunch of legislators pushing them to
                          sponsor the bill. For other kinds of Power Hour, such
                          as calls to the governor or calls not related to a
                          specific bill, this may not be useful.
                        </p>
                      </Popover.Body>
                    </Popover>
                  </Overlay>
                </div>
              </DetailLabel>
              <DetailContent>
                {powerHours == null ? (
                  'Loading...'
                ) : (
                  <>
                    {powerHours.length > 0 && (
                      <div className="mb-2">
                        {powerHours.map((p, i) => (
                          <div key={p.id}>
                            <a
                              href={p.spreadsheetUrl}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {p.title}
                            </a>
                            {i == powerHours.length - 1 && ' (latest)'}
                          </div>
                        ))}
                      </div>
                    )}
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
              </DetailContent>
            </>
          )}
          <DetailLabel>
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
                  <p>
                    You can keywords for the bill here, comma-separated. Then
                    all the <TwitterIcon style={{ width: '1rem' }} /> icons
                    above, next to the council members, will link to a search of
                    that council member&apos;s Twitter history for those terms.
                    (In the Power Hour spreadsheets, the{' '}
                    <em>Relevant tweets</em> links do these same searches.)
                  </p>
                  <p className="mb-0">
                    Note: Due to a Twitter bug, the Twitter search sometimes
                    displays 0 results even when there should be should be
                    matching tweets. Refreshing the Twitter page often fixes
                    this.
                  </p>
                </Popover.Body>
              </Popover>
            </Overlay>
          </DetailLabel>
          <DetailContent>
            <Form.Control
              type="text"
              placeholder="Enter comma-separated terms, e.g. solar, climate, fossil fuels"
              value={twitterSearchTermsRaw}
              onChange={handleTwitterSearchTermsChanged}
            />
          </DetailContent>
          <DetailLabel>Our notes</DetailLabel>
          <DetailContent>
            <Form.Control
              as="textarea"
              rows={3}
              value={formData.notes}
              placeholder="Add our notes about this bill"
              onChange={handleNotesChanged}
            />
          </DetailContent>
          {bill.type === 'CITY' && (
            <CityBillSponsorList
              bill={bill}
              twitterSearchTerms={formData.twitterSearchTerms}
            />
          )}
        </DetailTable>
        {bill.type === 'STATE' && (
          <div className={`${styles.fullWidth} mt-4 mb-3`}>
            <StateBillDetails
              bill={bill}
              twitterSearchTerms={formData.twitterSearchTerms}
            />
          </div>
        )}
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
          handleCloseWithoutConfirm={() => setShowDeleteBillConfirmation(false)}
        />
        <div style={{ fontStyle: 'italic' }}>{saveStatus}</div>
      </Form>
    </div>
  );
}
