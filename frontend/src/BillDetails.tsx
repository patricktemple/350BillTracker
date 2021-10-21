import React, { ReactElement, useState } from 'react';
import Button from 'react-bootstrap/Button';
import Stack from 'react-bootstrap/Stack';
import Form from 'react-bootstrap/Form';
import { Bill, BillSponsorship, BillAttachment } from './types';
import useInterval from '@restart/hooks/useInterval';
import useMountEffect from '@restart/hooks/useMountEffect';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import AddAttachmentModal from './AddAttachmentModal';
import { Link } from 'react-router-dom';
import useAutosavingFormData from './utils/useAutosavingFormData';
import ConfirmDeleteBillModel from './ConfirmDeleteBillModal';
import useApiFetch from './useApiFetch';
import { ReactComponent as TwitterIcon } from './assets/twitter.svg';

interface Props {
  bill: Bill;
  handleRemoveBill: () => void;
}

interface FormData {
  notes: string;
  nickname: string;
  twitterSearchTerms: string[];
}

export default function BillDetails(props: Props): ReactElement {
  const { bill } = props;

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/saved-bills/' + bill.id,
    {
      notes: bill.notes,
      nickname: bill.nickname,
      twitterSearchTerms: bill.twitterSearchTerms
    }
  );

  const [twitterSearchTermsRaw, setTwitterSearchTermsRaw] = useState<string>(
    bill.twitterSearchTerms.join(', ')
  );

  const [sponsorships, setSponsorships] = useState<
    BillSponsorship[] | null
  >(null);
  const [attachments, setAttachments] = useState<BillAttachment[] | null>(null);

  const [showDeleteBillConfirmation, setShowDeleteBillConfirmation] =
    useState<boolean>(false);

  const [addAttachmentModalOpen, setAddAttachmentModalOpen] =
    useState<boolean>(false);

  const [createPhoneBankInProgress, setCreatePhoneBankInProgress] =
    useState<boolean>(false);

  const apiFetch = useApiFetch();

  function loadAttachments() {
    apiFetch(`/api/saved-bills/${bill.id}/attachments`).then((response) => {
      setAttachments(response);
    });
  }

  useMountEffect(() => {
    apiFetch(`/api/saved-bills/${bill.id}/sponsorships`).then((response) => {
      setSponsorships(response);
    });
  });

  useMountEffect(() => {
    loadAttachments();
  });

  function handleNotesChanged(event: any) {
    setFormData({ ...formData, notes: event.target.value });
  }

  // TODO: Get real types for all my Events
  function handleNicknameChanged(event: any) {
    setFormData({ ...formData, nickname: event.target.value });
  }

  function handleTwitterSearchTermsChanged(event: any) {
    // Hmm this won't regenerate the twitter search links for all the sponsorships
    // Does that need to involve an async fetch of the latest terms?
    // Or just duplicate the logic on client side

    setTwitterSearchTermsRaw(event.target.value);
    const twitterSearchTermsList = event.target.value
      .split(',')
      .map((term: string) => term.trim())
      .filter(Boolean);
    setFormData({ ...formData, twitterSearchTerms: twitterSearchTermsList });
  }

  function handleAddAttachmentClicked(event: any) {
    setAddAttachmentModalOpen(true);
  }

  function handleAddAttachment(description: string, url: string) {
    setAddAttachmentModalOpen(false);
    apiFetch(`/api/saved-bills/${bill.id}/attachments`, {
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
    props.handleRemoveBill();
  }

  function handleGeneratePhoneBankSheet() {
    setCreatePhoneBankInProgress(true);
    apiFetch(`/api/saved-bills/${bill.id}/create-phone-bank-spreadsheet`, {
      method: 'POST'
    }).then((response) => {
      setCreatePhoneBankInProgress(false);
      loadAttachments();
    });
  }

  // This is confusing
  const positiveSponsors = sponsorships?.filter((s: BillSponsorship) => s.isSponsor);
  const negativeSponsors = sponsorships?.filter((s: BillSponsorship) => !s.isSponsor);
  return (
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          File:
        </Col>
        <Col>{bill.file}</Col>
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
        <Col>{bill.title}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Status:
        </Col>
        <Col>{bill.status}</Col>
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
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Sponsors {positiveSponsors != null && <>({positiveSponsors.length})</>}:
        </Col>
        <Col>
          {positiveSponsors == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {positiveSponsors.map((s) => (
                <div key={s.legislator.id}>
                  <Link to={'/council-members/' + s.legislator.id}>
                    {s.legislator.name}
                  </Link>{' '}
                  {s.twitterSearchUrl && (<span style={{ marginLeft: '0.5rem' }}>
                    <a
                      href={s.twitterSearchUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <TwitterIcon style={{width: '1rem'}}/>
                    </a>
                  </span>)}
                </div>
              ))}
            </Stack>
          )}
        </Col>
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Non-sponsors {negativeSponsors != null && <>({negativeSponsors.length})</>}:
        </Col>
        <Col>
          {negativeSponsors == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {negativeSponsors.map((s) => (
                <div key={s.legislator.id}>
                  <Link to={'/council-members/' + s.legislator.id}>
                    {s.legislator.name}
                  </Link>{' '}
                  {s.twitterSearchUrl && (<span style={{ marginLeft: '0.5rem' }}>
                    <a
                      href={s.twitterSearchUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <TwitterIcon style={{width: '1rem'}}/>
                    </a>
                  </span>)}
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
            <Button
              size="sm"
              disabled={createPhoneBankInProgress}
              variant="outline-secondary"
              onClick={handleGeneratePhoneBankSheet}
              className="mb-2 d-block"
            >
              {createPhoneBankInProgress
                ? 'Generating sheet...'
                : 'Create phone bank'}
            </Button>
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
      <Form.Group as={Row} className="mb-2">
        <Form.Label column lg={2} style={{ fontWeight: 'bold' }}>
          Twitter search terms:
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
