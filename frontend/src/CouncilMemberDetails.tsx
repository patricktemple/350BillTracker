import React from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { CouncilMember } from './types';

interface Props {
  councilMember: CouncilMember;
}

export default function CouncilMemberDetails(props: Props) {
  const member = props.councilMember;

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
  </Container>
  );
}