import React, { ReactElement, useState } from 'react';
import Stack from 'react-bootstrap/Stack';
import Form from 'react-bootstrap/Form';
import { Bill } from './types';
import useInterval from '@restart/hooks/useInterval';

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
      <Stack direction="vertical" gap={2}>
        <div>
          <strong>File:</strong> {bill.file}
        </div>
        <div>
          <strong>Title:</strong> {bill.title}
        </div>
        <div>
          <strong>Name:</strong> {bill.name}
        </div>
        <Form.Group className="mb-3">
          <Form.Label><strong>Nickname:</strong></Form.Label>
          <Form.Control type="text" size="sm" placeholder="Our short description of bill" value={billNickname} onChange={handleNicknameChanged} />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label><strong>Our notes:</strong></Form.Label>
          <Form.Control as="textarea" rows={3} size="sm" value={billNotes} placeholder="Add our notes about this bill" onChange={handleNotesChanged} />
        </Form.Group>
        <div>{getSaveText()}</div>
      </Stack>
    </Form>
  );
}