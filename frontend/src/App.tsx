import './App.css';
import { BrowserRouter as Router, Route } from "react-router-dom";
import SavedBillsPage from './SavedBillsPage';
import CouncilMembersPage from './CouncilMembersPage';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import React from 'react';

function App() {
  return (
    <Router>
      <Container>
        <Row>
          <Col lg={6}>
            <Nav defaultActiveKey="/" className="flex-column">
              <Nav.Link href="/">Bill campaigns</Nav.Link>
              <Nav.Link href="/council-members">Council members</Nav.Link>
            </Nav>
          </Col>
          <main>
            <Route path="/" exact component={SavedBillsPage} />
            <Route path="/council-members" component={CouncilMembersPage} />
          </main>
        </Row>
      </Container>
    </Router>
  )
}

export default App;
