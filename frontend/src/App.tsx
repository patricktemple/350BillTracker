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
import { MdPeople, MdDescription, MdSettings } from 'react-icons/md';
import styles from './style/App.module.scss';
import { Link } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className={styles.container}>
        <div className={styles.leftNavBackground} />
        <div className={styles.appTitle}>350 Brooklyn Bill Tracker</div>
        <Link to="/" className={styles.billsLogo}>
          <MdDescription />
        </Link>
        <Link to="/" className={styles.billsLink}>
          Bills
        </Link>
        <Link to="/council-members" className={styles.legislatorsLogo}>
          <MdPeople />
        </Link>
        <Link to="/council-members" className={styles.legislatorsLink}>
          Council members
        </Link>
        <Link to="/setting" className={styles.settingsLogo}>
          <MdSettings />
        </Link>
        <Link to="/settings" className={styles.settingsLink}>
          Settings
        </Link>
        <Link to="/logout" className={styles.logoutLogo}>
          <MdSettings />
        </Link>
        <Link to="/settings" className={styles.logoutLink}>
          Logout
        </Link>
        {/* <div className={styles.content}> */}
        <main className={styles.content}>
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
        {/* </div> */}
      </div>
    </Router>
  );
}

export default App;
