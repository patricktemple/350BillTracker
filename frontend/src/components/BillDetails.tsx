import React, { ReactElement, useState } from 'react';
import Button from 'react-bootstrap/Button';
import Stack from 'react-bootstrap/Stack';
import Form from 'react-bootstrap/Form';
import { Bill, SingleBillSponsorship, BillAttachment } from '../types';
import useInterval from '@restart/hooks/useInterval';
import useMountEffect from '@restart/hooks/useMountEffect';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import AddAttachmentModal from './AddAttachmentModal';
import { Link } from 'react-router-dom';
import useAutosavingFormData from '../utils/useAutosavingFormData';
import ConfirmDeleteBillModel from './ConfirmDeleteBillModal';

interface Props {
  bill: Bill;
  handleRemoveBill: () => void;
}

interface FormData {
  notes: string;
  nickname: string;
}

// TODO: Make a LazyAccordion that only renders its context the first time that
// it's visible, using useContext(AccordionContext). See this:
// https://react-bootstrap.github.io/components/accordion/
export default function BillDetails(props: Props): ReactElement {
  const { bill } = props;

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/saved-bills/' + bill.id,
    {
      notes: bill.notes,
      nickname: bill.nickname
    }
  );

  const [sponsorships, setSponsorships] = useState<
    SingleBillSponsorship[] | null
  >(null);
  const [attachments, setAttachments] = useState<BillAttachment[] | null>(null);

  const [showDeleteBillConfirmation, setShowDeleteBillConfirmation] =
    useState<boolean>(false);

  const [addAttachmentModalOpen, setAddAttachmentModalOpen] =
    useState<boolean>(false);

  const [createPhoneBankInProgress, setCreatePhoneBankInProgress] =
    useState<boolean>(false);

  function loadAttachments() {
    fetch(`/api/saved-bills/${bill.id}/attachments`)
      .then((response) => response.json())
      .then((response) => {
        setAttachments(response);
      });
  }

  // FIXME: This is loading all sponsorships individually on first page load of list
  useMountEffect(() => {
    console.log('Mount');
    fetch(`/api/saved-bills/${bill.id}/sponsorships`)
      .then((response) => response.json())
      .then((response) => {
        setSponsorships(response);
      });
  });

  // FIXME: This is loading all attachments individually on first page load of list
  useMountEffect(() => {
    loadAttachments();
  });

  function handleNotesChanged(event: any) {
    setFormData({ ...formData, notes: event.target.value });
  }

  function handleNicknameChanged(event: any) {
    setFormData({ ...formData, nickname: event.target.value });
  }

  function handleAddAttachmentClicked(event: any) {
    setAddAttachmentModalOpen(true);
  }

  function handleAddAttachment(description: string, url: string) {
    setAddAttachmentModalOpen(false);
    fetch(`/api/saved-bills/${bill.id}/attachments`, {
      method: 'POST',
      body: JSON.stringify({ url, name: description }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((response) => {
        loadAttachments();
      });
  }

  function handleDeleteAttachment(event: any, id: number) {
    event.preventDefault();
    fetch(`/api/saved-bills/-/attachments/` + id, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((response) => {
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
    fetch(`/api/saved-bills/${bill.id}/create-phone-bank-spreadsheet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((response) => {
        setCreatePhoneBankInProgress(false);
        loadAttachments();
      });
  }

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
          Sponsors {sponsorships != null && <>({sponsorships.length})</>}:
        </Col>
        <Col>
          {sponsorships == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {sponsorships.map((s) => (
                <Link
                  to={'/council-members/' + s.legislator.id}
                  key={s.legislator.id}
                >
                  {s.legislator.name}
                </Link>
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
              variant="outline-primary"
              onClick={handleAddAttachmentClicked}
              className="mt-2 mb-2"
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
              variant="outline-primary"
              onClick={handleGeneratePhoneBankSheet}
              className="mb-2"
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
            variant="outline-primary"
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
