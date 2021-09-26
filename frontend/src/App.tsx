import './App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import SavedBillsPage from './SavedBillsPage';
import CouncilMembersPage from './CouncilMembersPage';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const colors = {
  brown: "#584B53",
  copper: "#9D5C63",
  blue: "#D6E3F8",
  beige: "#FEF5EF",
  sand: "#E4BB97"
};


const styles ={
  container: {
    height: '100%',
    width: '100%',
    display: 'grid',
    gridTemplateRows: '100px 1fr',
    gridTemplateColumns: '200px 1fr',
  },
  leftNav: {
    backgroundColor: colors.beige,
    gridRow: "2 / span 1",
    gridColumn: "1 / span 1",
    padding: "20px",
  },
  heading: {
    padding: "20px",
    gridColumn: "1 / span 2",
    gridRow: "1 / span 1",
  },
  mainContent: {
    gridColumn: "2 / span 1",
    gridRow: "2 / span 1",
    padding: "20px",
  },
}

function App() {
  return (
    <Router>
      <div style={styles.container}>
        <div style={styles.heading}>
          <h1 className="mb-4 red">350 Brooklyn Bill Tracker</h1>
        </div>
        <div style={styles.leftNav}>
          <Nav defaultActiveKey="/" className="flex-column">
            <Nav.Link href="/">Bill campaigns</Nav.Link>
            <Nav.Link href="/council-members">Council members</Nav.Link>
          </Nav>
        </div>
        <div style={styles.mainContent}>
          <main>
            <Route path="/" exact>
              <Redirect to="/saved-bills" />
            </Route>
            <Route
              path="/saved-bills/:billId?"
              exact
              component={SavedBillsPage}
            />
            <Route
              path="/council-members/:memberId?"
              component={CouncilMembersPage}
            />
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
