import './App.css';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
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
          <Col md={true}>
            <h1 className="mb-4">350 Brooklyn Bill Tracker</h1>
          </Col>
        </Row>
        <Row>
          <Col md={3}>
            <Nav defaultActiveKey="/" className="flex-column">
              <Nav.Link href="/">Bill campaigns</Nav.Link>
              <Nav.Link href="/council-members">Council members</Nav.Link>
            </Nav>
          </Col>
          <Col>
            <main>
              <Route path="/" exact>
                <Redirect to="/saved-bills" />
              </Route>
              <Route
                path="/saved-bills/:billId?"
                exact
                component={SavedBillsPage}
              />
              <Route path="/council-members" component={CouncilMembersPage} />
            </main>
          </Col>
        </Row>
      </Container>
    </Router>
  );
}

export default App;
