import React, { useState, useRef, ReactElement } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Bill, CreatePowerHourResponse, PowerHour } from './types';
import Modal from 'react-bootstrap/Modal';
import useApiFetch from './useApiFetch';
import { MdHelpOutline } from 'react-icons/md';
import Alert from 'react-bootstrap/Alert';
import Popover from 'react-bootstrap/Popover';
import Overlay from 'react-bootstrap/Overlay';
import moment from 'moment';

interface ModalProps {
  bill: Bill;
  oldPowerHours: PowerHour[];
  show: boolean;
  handlePowerHourCreated: () => void;
  onHide: () => void;
}

interface BodyProps {
  bill: Bill;
  oldPowerHours: PowerHour[];
  handlePowerHourCreated: () => void;
  onHide: () => void;
}

const DO_NOT_IMPORT_VALUE = 'none';

// Separate the body out from the modal so that it's recreated whenever the modal
// disappears and reappears (in order to refresh its state).
function PowerHourModalBody(props: BodyProps): ReactElement {
  const titleRef = useRef<HTMLInputElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);
  const helpIconRef = useRef<HTMLSpanElement>(null);

  const [createPowerHourInProgress, setCreatePowerHourInProgress] =
    useState<boolean>(false);
  const [createPowerHourMessages, setCreatePowerHourMessages] = useState<
    string[]
  >([]);
  const [powerHourResult, setPowerHourResult] = useState<PowerHour | null>(
    null
  );
  const [importHelpShown, setImportHelpShown] = useState<boolean>(false);

  // Once modal opens, don't refresh the list of old power hours. Otherwise,
  // the new one will appear in the "old power hours" list as soon after it's
  // created, which is confusing.
  const [oldPowerHours] = useState<PowerHour[]>(props.oldPowerHours);

  const apiFetch = useApiFetch();

  const defaultTitle = `Power Hour for ${props.bill.cityBill!.file} (${moment().format(
    'MMM D YYYY'
  )})`;
  const lastWeekText = moment().subtract(7, 'days').format('MM/D');

  function handleSubmit(e: any) {
    const title = titleRef.current!.value;
    const selectValue = selectRef.current!.value;

    setCreatePowerHourInProgress(true);
    apiFetch(`/api/saved-bills/${props.bill.id}/power-hours`, {
      method: 'POST',
      body: {
        title,
        powerHourIdToImport:
          selectValue !== DO_NOT_IMPORT_VALUE ? selectValue : null
      }
    }).then((response: CreatePowerHourResponse) => {
      setCreatePowerHourMessages(response.messages);
      setCreatePowerHourInProgress(false);
      setPowerHourResult(response.powerHour);
      props.handlePowerHourCreated();
    });

    e.preventDefault();
  }

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3">
        <Form.Label>Spreadsheet title</Form.Label>
        <Form.Control
          type="text"
          ref={titleRef}
          defaultValue={defaultTitle}
          disabled={createPowerHourInProgress || !!powerHourResult}
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>
          Copy data from previous power hour{' '}
          <span
            style={{ cursor: 'pointer' }}
            ref={helpIconRef}
            onClick={() => setImportHelpShown(!importHelpShown)}
          >
            <MdHelpOutline />
          </span>
        </Form.Label>
        <Overlay
          target={helpIconRef.current}
          show={importHelpShown}
          placement="right"
        >
          <Popover style={{ width: '600px', maxWidth: '600px' }}>
            <Popover.Header as="h3">
              Importing from old spreadsheets
            </Popover.Header>
            <Popover.Body>
              <p>
                When you create a Power Hour, it generates a new Google Sheet
                with the latest sponsor list and contact info.
              </p>
              <p>
                However, you may want to carry over some information from this
                bill&apos;s previous power hour into the new spreadsheet. For
                example, suppose that that last week had a power hour on the
                same bill, and that spreadsheet had added a column called{' '}
                <em>Summary of action {lastWeekText}</em> to track how the
                conversation went with each concil member. You can import that
                column into the new spreadsheet so that new callers have that
                context.
              </p>
              <p>
                Importing from an old spreadsheet works like this:
                <ol>
                  <li>You choose which sheet to import from, if any</li>
                  <li>
                    The tool looks for a <em>Name</em> column in the top row of
                    the old sheet. It uses this column to find each council
                    member by an exact match of their name.
                  </li>
                  <li>
                    If any extra columns were added to the old sheet, those are
                    copied into the new sheet next to the correct council
                    member.
                  </li>
                  <li>
                    Auto-generated columns (such as Twitter, phone number) are
                    recreated fresh in the new sheet.
                  </li>
                </ol>
              </p>
            </Popover.Body>
          </Popover>
        </Overlay>
        <Form.Select
          ref={selectRef}
          disabled={
            createPowerHourInProgress ||
            !!powerHourResult ||
            oldPowerHours.length == 0
          }
        >
          {oldPowerHours.length > 0 &&
            oldPowerHours.map((p, i) => (
              <option
                key={p.id}
                value={p.id}
                selected={i === oldPowerHours.length - 1}
              >
                {p.title}
                {i == oldPowerHours.length - 1 && ' (latest)'}
              </option>
            ))}
          <option value={DO_NOT_IMPORT_VALUE}>
            {oldPowerHours.length > 0
              ? 'Do not import'
              : 'This bill has no previous power hours'}
          </option>
        </Form.Select>
      </Form.Group>

      {powerHourResult ? (
        <>
          <Alert variant="primary">
            <p>
              {createPowerHourMessages.map((m) => (
                <div key={m}>{m}</div>
              ))}
            </p>
            <p className="mb-0" style={{ fontWeight: 'bold' }}>
              <a
                href={powerHourResult.spreadsheetUrl}
                rel="noreferrer"
                target="_blank"
              >
                Open spreadsheet
              </a>
            </p>
          </Alert>
          <Button variant="primary" className="mb-2" onClick={props.onHide}>
            Close
          </Button>
        </>
      ) : (
        <Button
          variant="primary"
          type="submit"
          className="mb-2"
          disabled={createPowerHourInProgress || !!powerHourResult}
        >
          {createPowerHourInProgress ? 'Generating...' : 'Generate spreadsheet'}
        </Button>
      )}
    </Form>
  );
}

export default function CreatePowerHourModal(props: ModalProps): ReactElement {
  return (
    <Modal show={props.show} onHide={props.onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Create a Power Hour</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <PowerHourModalBody
          bill={props.bill}
          onHide={props.onHide}
          handlePowerHourCreated={props.handlePowerHourCreated}
          oldPowerHours={props.oldPowerHours}
        />
      </Modal.Body>
    </Modal>
  );
}
