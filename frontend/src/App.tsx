import './style/App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import SavedBillsPage from './SavedBillsPage';
import LegislatorsPage from './LegislatorsPage';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import React from 'react';
// import 'bootstrap/dist/css/bootstrap.min.css';
import { MdPeople, MdDescription } from 'react-icons/md';
import styles from './style/App.module.scss';

function App() {
  return (
    <Router>
      <div className={styles.container}>
        <div className={styles.heading}>350 Brooklyn Bill Tracker</div>
        <div className={styles.leftNav}>
          <Nav defaultActiveKey="/" className="flex-column">
            <Nav.Link href="/" className={styles.navLink}>
              <MdDescription className={styles.icon} />
              Bills
            </Nav.Link>
            <Nav.Link href="/council-members" className={styles.navLink}>
              <MdPeople className={styles.icon} />
              Council members
            </Nav.Link>
          </Nav>
        </div>
        <div className={styles.mainContent}>
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
