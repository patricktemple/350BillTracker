import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { CouncilMember, SingleMemberSponsorship } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Stack from 'react-bootstrap/Stack';
import { Link } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import useAutosavingFormData from './utils/useAutosavingFormData';

interface Props {
  councilMember: CouncilMember;
}

interface FormData {
  notes: string;
}

export default function CouncilMemberDetails(props: Props) {
  const member = props.councilMember;

  const [sponsorships, setSponsorships] = useState<
    SingleMemberSponsorship[] | null
  >(null);

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>('/api/council-members/' + member.id, { notes: member.notes } );

  // FIXME: This is loading all sponsorships individually on first page load of list
  useMountEffect(() => {
    fetch(`/api/council-members/${member.id}/sponsorships`)
      .then((response) => response.json())
      .then((response) => {
        setSponsorships(response);
      });
  });

  function handleNotesChanged(e: any) {
    setFormData({ ...formData, notes: e.target.value });
  }

  return (
    <Form onSubmit={(e) => e.preventDefault()}>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Name:</strong>
        </Col>
        <Col>{member.name}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Email:</strong>
        </Col>
        <Col>{member.email}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>District phone:</strong>
        </Col>
        <Col>{member.districtPhone}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Legislative phone:</strong>
        </Col>
        <Col>{member.legislativePhone}</Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <strong>Website:</strong>
        </Col>
        <Col>
          {member.website && <a href={member.website}>Visit website</a>}
        </Col>
      </Row>
      <Row className="mb-2">
        <Col lg={2}>
          <>
            <div style={{fontWeight: 'bold'}}>
              Sponsored bills
            </div>
            <div>
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
        <Form.Label column lg={2}>
          <strong>Our notes:</strong>
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
      <div style={{fontStyle: 'italics'}}>
        {saveStatus}
      </div>
    </Form>
  );
}
