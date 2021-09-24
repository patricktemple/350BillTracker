import React, { ReactElement, useState } from 'react';
import Stack from 'react-bootstrap/Stack';
import Form from 'react-bootstrap/Form';
import { Bill, SingleBillSponsorship } from './types';
import useInterval from '@restart/hooks/useInterval';
import useMountEffect from '@restart/hooks/useMountEffect';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

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

  const [sponsorships, setSponsorships] = useState<SingleBillSponsorship[] | null>(null);

  // FIXME: This is loading all sponsorships individually on first page load of list
  useMountEffect(() => {
    fetch(`/api/saved-bills/${bill.id}/sponsorships`)
      .then((response) => response.json())
      .then((response) => {
          setSponsorships(response);
      });
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
      return "Draft";
    }
    if (saveInProgress) {
      return "Saving...";
    }
    if (remoteSaveVersion > 0) {
      return "Saved";
    }

    return null;
  }

  return (
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2}><strong>File:</strong></Col>
        <Col>{bill.file}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}><strong>Title:</strong></Col>
        <Col>{bill.title}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}><strong>Name:</strong></Col>
        <Col>{bill.name}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}><strong>Sponsors {sponsorships != null && <>({sponsorships.length})</>}:</strong></Col>
        <Col>
          {sponsorships == null ? "Loading..." : (
            <Stack direction="vertical">
              {sponsorships.map(s => <div key={s.legislator.id}>{s.legislator.name}</div>)}
            </Stack>
          )}
        </Col>
      </Row>

      <Form.Group as={Row} className="mb-2">
          <Form.Label column lg={2}><strong>Nickname:</strong></Form.Label>
          <Col>
            <Form.Control type="text" size="sm" placeholder="Our short description of bill" value={billNickname} onChange={handleNicknameChanged} />
          </Col>
        </Form.Group>
        <Form.Group as={Row} className="mb-2">
          <Form.Label column lg={2}><strong>Our notes:</strong></Form.Label>
          <Col>
            <Form.Control as="textarea" rows={3} size="sm" value={billNotes} placeholder="Add our notes about this bill" onChange={handleNotesChanged} />
          </Col>
        </Form.Group>
        <div><em>{getSaveText()}</em></div>
    </Form>
  );
}