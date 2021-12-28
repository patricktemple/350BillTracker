import React, { ReactElement, useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Stack from 'react-bootstrap/Stack';
import Form from 'react-bootstrap/Form';
import { Bill, CitySponsorship, BillAttachment, PowerHour } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import AddAttachmentModal from './AddAttachmentModal';
import useAutosavingFormData from './utils/useAutosavingFormData';
import ConfirmDeleteBillModel from './ConfirmDeleteBillModal';
import CreatePowerHourModal from './CreatePowerHourModal';
import useApiFetch from './useApiFetch';
import BillSponsorList from './BillSponsorList';
import Popover from 'react-bootstrap/Popover';
import Overlay from 'react-bootstrap/Overlay';
import { MdHelpOutline } from 'react-icons/md';

import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

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

  const [sponsorships, setSponsorships] = useState<CitySponsorship[] | null>(
    null
  );
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
        twitterSearchTerms: response.twitterSeachTerms
      });
      setTwitterSearchTermsRaw(response.twitterSearchTerms.join(','));
    });
    apiFetch(`/api/city-bills/${billId}/sponsorships`).then((response) => {
      setSponsorships(response);
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
      window.alert('bill is gone');
      // TODO
    });
  }

  function handlePowerHourCreated() {
    loadPowerHours();
  }

  const positiveSponsors = sponsorships?.filter(
    (s: CitySponsorship) => s.isSponsor
  );
  const negativeSponsors = sponsorships?.filter(
    (s: CitySponsorship) => !s.isSponsor
  );

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
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          File:
        </Col>
        <Col>{bill.cityBill!.file}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Official name:
        </Col>
        <Col>{bill.name}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Description:
        </Col>
        <Col>{bill.cityBill!.title}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Status:
        </Col>
        <Col>{bill.cityBill!.status}</Col>
      </Row>
      <Form.Group as={Row} className="mb-2">
        <Form.Label column lg={2} style={{ fontWeight: 'bold' }}>
          Our nickname:
        </Form.Label>
        <Col>
          <Form.Control
            type="text"
            size="sm"
            placeholder='e.g. "Skip the stuff"'
            value={formData.nickname}
            onChange={handleNicknameChanged}
          />
        </Col>
      </Form.Group>
      <Row className="mb-2">
        <Col lg={2}>
          <div style={{ fontWeight: 'bold' }}>
            Sponsors{' '}
            {positiveSponsors != null && <>({positiveSponsors.length})</>}:
          </div>
          <div style={{ fontSize: '0.8rem', fontStyle: 'italic' }}>
            Note: Due to a Twitter bug, the Twitter search sometimes displays 0
            results even when there should be should be matching tweets.
            Refreshing the Twitter page often fixes this.
          </div>
        </Col>
        <Col>
          {positiveSponsors == null ? (
            'Loading...'
          ) : (
            <BillSponsorList
              sponsorships={positiveSponsors}
              twitterSearchTerms={formData.twitterSearchTerms}
            />
          )}
        </Col>
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Non-sponsors{' '}
          {negativeSponsors != null && <>({negativeSponsors.length})</>}:
        </Col>
        <Col>
          {negativeSponsors == null ? (
            'Loading...'
          ) : (
            <BillSponsorList
              sponsorships={negativeSponsors}
              twitterSearchTerms={formData.twitterSearchTerms}
            />
          )}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <div>
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
        </Col>
        <Col>
          {attachments == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {attachments.map((a) => (
                <div key={a.id}>
                  <a href={a.url} target="attachment">
                    {a.name}
                  </a>
                  &nbsp;
                  <a href="#" onClick={(e) => handleDeleteAttachment(e, a.id)}>
                    [Remove]
                  </a>
                </div>
              ))}
            </Stack>
          )}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
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
                    These sheets are designed for Power Hours involving calls to
                    a bunch of legislators pushing them to sponsor the bill. For
                    other kinds of Power Hour, such as calls to the governor or
                    calls not related to a specific bill, this may not be
                    useful.
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
        </Col>
        <Col>
          {powerHours == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {powerHours.map((p, i) => (
                <div key={p.id}>
                  <a href={p.spreadsheetUrl} target="_blank" rel="noreferrer">
                    {p.title}
                  </a>
                  {i == powerHours.length - 1 && ' (latest)'}
                </div>
              ))}
            </Stack>
          )}
        </Col>
      </Row>
      <Form.Group as={Row} className="mb-2">
        <Form.Label column lg={2} style={{ fontWeight: 'bold' }}>
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
                  You can keywords for the bill here, comma-separated. Then all
                  the <TwitterIcon style={{ width: '1rem' }} /> icons above,
                  next to the council members, will link to a search of that
                  council member&apos;s Twitter history for those terms. (In the
                  Power Hour spreadsheets, the <em>Relevant tweets</em> links do
                  these same searches.)
                </p>
              </Popover.Body>
            </Popover>
          </Overlay>
        </Form.Label>
        <Col>
          <Form.Control
            type="text"
            size="sm"
            placeholder="Enter comma-separated terms, e.g. solar, climate, fossil fuels"
            value={twitterSearchTermsRaw}
            onChange={handleTwitterSearchTermsChanged}
          />
        </Col>
      </Form.Group>
      <Form.Group as={Row} className="mb-2">
        <Form.Label column lg={2} style={{ fontWeight: 'bold' }}>
          Our notes:
        </Form.Label>
        <Col>
          <Form.Control
            as="textarea"
            rows={3}
            size="sm"
            value={formData.notes}
            placeholder="Add our notes about this bill"
            onChange={handleNotesChanged}
          />
        </Col>
      </Form.Group>
      <Row className="mt-3 mb-2">
        <Col>
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
        </Col>
      </Row>
      <div style={{ fontStyle: 'italic' }}>{saveStatus}</div>
    </Form>
  );
}
