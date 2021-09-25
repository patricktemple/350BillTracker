import React, { ReactElement, useState } from 'react';
import Button from 'react-bootstrap/Button';
import Stack from 'react-bootstrap/Stack';
import Form from 'react-bootstrap/Form';
import { Bill, SingleBillSponsorship, BillAttachment } from './types';
import useInterval from '@restart/hooks/useInterval';
import useMountEffect from '@restart/hooks/useMountEffect';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import AddAttachmentModal from './AddAttachmentModal';
import { Link } from 'react-router-dom';

interface Props {
  bill: Bill;
}

export default function BillDetails(props: Props): ReactElement {
  const { bill } = props;

  const [billNotes, setBillNotes] = useState<string>(bill.notes);
  const [billNickname, setBillNickname] = useState<string>(bill.nickname);

  const [localSaveVersion, setLocalSaveVersion] = useState<number>(0);
  const [remoteSaveVersion, setRemoteSaveVersion] = useState<number>(0);
  const [saveInProgress, setSaveInProgress] = useState<boolean>(false);

  const [sponsorships, setSponsorships] = useState<
    SingleBillSponsorship[] | null
  >(null);
  const [attachments, setAttachments] = useState<BillAttachment[] | null>(null);

  const [addAttachmentModalOpen, setAddAttachmentModalOpen] =
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

  // TODO: Handle save failure too!
  function maybeSaveUpdates() {
    if (localSaveVersion > remoteSaveVersion && !saveInProgress) {
      setSaveInProgress(true);
      setRemoteSaveVersion(localSaveVersion);
      fetch('/api/saved-bills/' + bill.id, {
        method: 'PUT',
        body: JSON.stringify({ notes: billNotes, nickname: billNickname }),
        headers: {
          'Content-Type': 'application/json'
        }
      })
        .then((response) => response.json())
        .then((response) => {
          setSaveInProgress(false);
        });
    }
  }

  useInterval(() => maybeSaveUpdates(), 2000);

  function handleNotesChanged(e: any) {
    setBillNotes(e.target.value);
    setLocalSaveVersion(localSaveVersion + 1);
  }

  function handleNicknameChanged(e: any) {
    setBillNickname(e.target.value);
    setLocalSaveVersion(localSaveVersion + 1);
  }

  function getSaveText() {
    if (localSaveVersion > remoteSaveVersion) {
      return 'Draft';
    }
    if (saveInProgress) {
      return 'Saving...';
    }
    if (remoteSaveVersion > 0) {
      return 'Saved';
    }

    return null;
  }

  function handleAddAttachmentClicked(e: any) {
    setAddAttachmentModalOpen(true);
    e.preventDefault();
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

  return (
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>File:</strong>
        </Col>
        <Col>{bill.file}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Official name:</strong>
        </Col>
        <Col>{bill.name}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Description:</strong>
        </Col>
        <Col>{bill.title}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Status:</strong>
        </Col>
        <Col>{bill.status}</Col>
      </Row>
      <Form.Group as={Row} className="mb-2">
        <Form.Label column lg={2}>
          <strong>Our nickname:</strong>
        </Form.Label>
        <Col>
          <Form.Control
            type="text"
            size="sm"
            placeholder='e.g. "Skip the stuff"'
            value={billNickname}
            onChange={handleNicknameChanged}
          />
        </Col>
      </Form.Group>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>
            Sponsors {sponsorships != null && <>({sponsorships.length})</>}:
          </strong>
        </Col>
        <Col>
          {sponsorships == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {sponsorships.map((s) => (
                <Link to={'/council-members/' + s.legislator.id} key={s.legislator.id}>{s.legislator.name}</Link>
              ))}
            </Stack>
          )}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <Stack direction="vertical">
            <div>
              <strong>Attachments:</strong>
            </div>
            <a href="#" onClick={handleAddAttachmentClicked}>
              Attach a link
            </a>
            <AddAttachmentModal
              show={addAttachmentModalOpen}
              handleAddAttachment={handleAddAttachment}
              onHide={() => setAddAttachmentModalOpen(false)}
            />
          </Stack>
        </Col>
        <Col>
          {attachments == null ? (
            'Loading...'
          ) : attachments.length == 0 ? (
            <em>(none)</em>
          ) : (
            <Stack direction="vertical">
              {attachments.map((a) => (
                <div key={a.id}>
                  <a href={a.url} target="attachment">
                    {a.name}
                  </a>
                </div>
              ))}
            </Stack>
          )}
        </Col>
      </Row>
      <Form.Group as={Row} className="mb-2">
        <Form.Label column lg={2}>
          <strong>Our notes:</strong>
        </Form.Label>
        <Col>
          <Form.Control
            as="textarea"
            rows={3}
            size="sm"
            value={billNotes}
            placeholder="Add our notes about this bill"
            onChange={handleNotesChanged}
          />
        </Col>
      </Form.Group>
      <div>
        <em>{getSaveText()}</em>
      </div>
    </Form>
  );
}
