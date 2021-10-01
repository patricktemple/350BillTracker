import './App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import SavedBillsPage from './SavedBillsPage';
import LegislatorsPage from './LegislatorsPage';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { MdPeople, MdDescription } from 'react-icons/md';
import LoginPage from './LoginPage';

// TODO: Fix palette
const colors = {
  // brown: "#584B53",
  // copper: "#9D5C63",
  mediumBlue: '#D6E3F8',
  // beige: "#FEF5EF",
  // sand: "#E4BB97"
  lightBlue: '#e7f1ff'
};

const styles = {
  container: {
    height: '100%',
    width: '100%',
    display: 'grid',
    gridTemplateRows: '70px 1fr',
    gridTemplateColumns: '280px 1fr'
  },
  leftNav: {
    backgroundColor: colors.lightBlue,
    gridRow: '2 / span 1',
    gridColumn: '1 / span 1',
    padding: '20px'
  },
  heading: {
    padding: '16px 20px',
    gridColumn: '1 / span 2',
    gridRow: '1 / span 1',
    fontSize: '1.5rem',
    'font-weight': '500',
    backgroundColor: colors.mediumBlue
  },
  mainContent: {
    gridColumn: '2 / span 1',
    gridRow: '2 / span 1',
    padding: '20px'
  },
  navLink: {
    fontSize: '1.3rem',
    padding: '0 0 0.8rem 0'
  },
  icon: {
    marginRight: '8px',
    width: '1.3rem',
    height: '1.3rem'
  }
};

function App() {
  const [loggedIn, setLoggedIn] = useState<boolean>();

  if (!loggedIn) {
    return <LoginPage login={() => setLoggedIn(true)}/>;
  }

  return (
    <Router>
      <div style={styles.container}>
        <div style={styles.heading}>350 Brooklyn Bill Tracker</div>
        <div style={styles.leftNav}>
          <Nav defaultActiveKey="/" className="flex-column">
            <Nav.Link href="/" style={styles.navLink}>
              <MdDescription style={styles.icon} />
              Bills
            </Nav.Link>
            <Nav.Link href="/council-members" style={styles.navLink}>
              <MdPeople style={styles.icon} />
              Council members
            </Nav.Link>
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
              path="/council-members/:legislatorId?"
              component={LegislatorsPage}
            />
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
