import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { CouncilMember, SingleMemberSponsorship } from './types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Stack from 'react-bootstrap/Stack';

interface Props {
  councilMember: CouncilMember;
}

export default function CouncilMemberDetails(props: Props) {
  const member = props.councilMember;

  const [sponsorships, setSponsorships] = useState<SingleMemberSponsorship[] | null>(null);

  // FIXME: This is loading all sponsorships individually on first page load of list
  useMountEffect(() => {
    fetch(`/api/council-members/${member.id}/sponsorships`)
      .then((response) => response.json())
      .then((response) => {
        setSponsorships(response);
      });
  });

  return (
  <Container>
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
      <><strong>
        Sponsored bills</strong> (only includes bills we are tracking)</>
    </Col>
    <Col>
      {sponsorships == null ? (
        'Loading...'
      ) : (
        <Stack direction="vertical">
          {sponsorships.map((s) => (
            <div key={s.bill.id}>{s.bill.name}</div>
          ))}
        </Stack>
      )}
    </Col>
  </Row>
  </Container>
  );
}