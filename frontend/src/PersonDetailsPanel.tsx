import React, { useState, ReactElement } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { Person, SingleMemberSponsorship, Staffer, Uuid } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Stack from 'react-bootstrap/Stack';
import { Link } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import useAutosavingFormData from './utils/useAutosavingFormData';
import useApiFetch from './useApiFetch';
import Button from 'react-bootstrap/Button';
import AddStafferModal from './AddStafferModal';

interface Props {
  person: Person;
}

interface FormData {
  notes: string;
}

function formatStaffer(staffer: Staffer) {
  const contactElements: (string | ReactElement)[] = [
    staffer.phone,
    staffer.email
  ].filter((item) => !!item);
  if (staffer.twitter) {
    contactElements.push(
      <a href={`https://www.twitter.com/${staffer.twitter}`}>
        @{staffer.twitter}
      </a>
    );
  }
  const contactString =
    contactElements.length == 0
      ? 'No contact info'
      : contactElements.map((item, i) => (
          <>
            {item}
            {i < contactElements.length - 1 && ', '}
          </>
        ));

  return (
    <>
      {staffer.title && <>{staffer.title} - </>}
      {staffer.name} ({contactString})
    </>
  );
}

export default function PersonDetailsPanel(props: Props) {
  const person = props.person;

  const [sponsorships, setSponsorships] = useState<
    SingleMemberSponsorship[] | null
  >(null);
  const [staffers, setStaffers] = useState<Staffer[] | null>(null);
  const [addStafferModalVisible, setAddStafferModalVisible] =
    useState<boolean>(false);

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/persons/' + person.id,
    { notes: person.notes }
  );
  const apiFetch = useApiFetch();

  function loadStaffers() {
    apiFetch(`/api/persons/${person.id}/staffers`).then((response) => {
      setStaffers(response);
    });
  }

  useMountEffect(() => {
    // apiFetch(`/api/council-members/${person.id}/sponsorships`).then(
    //   (response) => {
    //     setSponsorships(response);
    //   }
    // );
    loadStaffers();
  });

  function handleNotesChanged(event: any) {
    setFormData({ ...formData, notes: event.target.value });
  }

  function handleAddStaffer(
    name: string,
    title: string,
    phone: string,
    email: string,
    twitter: string
  ) {
    setAddStafferModalVisible(false);
    apiFetch(`/api/persons/${person.id}/staffers`, {
      method: 'POST',
      body: {
        name: name || null,
        title: title || null,
        phone: phone || null,
        email: email || null,
        twitter: twitter || null
      }
    }).then((response) => {
      loadStaffers();
    });
  }

  function handleRemoveStaffer(e: any, id: Uuid) {
    e.preventDefault();
    // TODO: Show a confirmation?
    apiFetch(`/api/persons/-/staffers/` + id, {
      method: 'DELETE'
    }).then((response) => {
      loadStaffers();
    });
  }

  // should rewrite this w/o bootstrap grid
  return (
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Name:
        </Col>
        <Col>{person.name}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Email:
        </Col>
        <Col>{person.email}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          District phone:
        </Col>
        <Col>{person.phone}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Legislative phone:
        </Col>
        <Col>{person.councilMember!.legislativePhone}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Party:
        </Col>
        <Col>{person.party}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Website:
        </Col>
        <Col>
          {person.councilMember!.website && (
            <a href={person.councilMember!.website} target="website">
              Visit website
            </a>
          )}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Twitter:
        </Col>
        <Col>
          {person.twitter && (
            <a href={`https://twitter.com/${person.twitter}`} target="twitter">
              @{person.twitter}
            </a>
          )}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Staffers:
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={() => setAddStafferModalVisible(true)}
            className="mt-2 mb-2 d-block"
          >
            Add staffer
          </Button>
        </Col>
        <Col>
          {staffers &&
            staffers.map((staffer) => (
              <div key={staffer.id}>
                {formatStaffer(staffer)} [
                <a href="#" onClick={(e) => handleRemoveStaffer(e, staffer.id)}>
                  Delete
                </a>
                ]
              </div>
            ))}
        </Col>
        <AddStafferModal
          show={addStafferModalVisible}
          handleAddStaffer={handleAddStaffer}
          onHide={() => setAddStafferModalVisible(false)}
        />
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <>
            <div style={{ fontWeight: 'bold' }}>Sponsored bills</div>
            <div style={{ fontStyle: 'italic' }}>
              Only includes bills we are tracking
            </div>
          </>
        </Col>
        <Col>
          {sponsorships == null ? (
            'Loading...'
          ) : (
            <Stack direction="vertical">
              {sponsorships.map((s) => (
                <Link to={'/saved-bills/' + s.bill.id} key={s.bill.id}>
                  {s.bill.cityBill!.file}:{' '}
                  <em>{s.bill.nickname || s.bill.name}</em>
                </Link>
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
            placeholder="Add our notes about this person"
            onChange={handleNotesChanged}
          />
        </Col>
      </Form.Group>
      <div style={{ fontStyle: 'italic' }}>{saveStatus}</div>
    </Form>
  );
}
