import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { Legislator, SingleMemberSponsorship } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Stack from 'react-bootstrap/Stack';
import { Link } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import useAutosavingFormData from './utils/useAutosavingFormData';

interface Props {
  legislator: Legislator;
}

interface FormData {
  notes: string;
}

export default function LegislatorDetailsPanel(props: Props) {
  const legislator = props.legislator;

  const [sponsorships, setSponsorships] = useState<
    SingleMemberSponsorship[] | null
  >(null);

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/legislators/' + legislator.id,
    { notes: legislator.notes }
  );

  // FIXME: This is loading all sponsorships individually on first page load of list
  useMountEffect(() => {
    fetch(`/api/legislators/${legislator.id}/sponsorships`)
      .then((response) => response.json())
      .then((response) => {
        setSponsorships(response);
      });
  });

  function handleNotesChanged(event: any) {
    setFormData({ ...formData, notes: event.target.value });
  }

  return (
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Name:
        </Col>
        <Col>{legislator.name}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Email:
        </Col>
        <Col>{legislator.email}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          District phone:
        </Col>
        <Col>{legislator.districtPhone}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Legislative phone:
        </Col>
        <Col>{legislator.legislativePhone}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Party:
        </Col>
        <Col>{legislator.party}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Website:
        </Col>
        <Col>
          {legislator.website && <a href={legislator.website}>Visit website</a>}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2} style={{ fontWeight: 'bold' }}>
          Twitter:
        </Col>
        <Col>
          <a href={`https://twitter.com/${legislator.twitter}`}>
            @{legislator.twitter}
          </a>
        </Col>
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
                  {s.bill.file}: <em>{s.bill.nickname || s.bill.name}</em>
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
