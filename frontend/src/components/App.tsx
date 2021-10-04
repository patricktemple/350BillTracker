import '../style/App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import BillsPage from './BillsPage';
import LegislatorsPage from './LegislatorsPage';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import React from 'react';
import styles from '../style/App.module.scss';
import { Link } from 'react-router-dom';
import { ReactComponent as SettingsIcon } from '../assets/settings.svg';
import { ReactComponent as LogoutIcon } from '../assets/logout.svg';
import { ReactComponent as BillsIcon } from '../assets/paper.svg';
import { ReactComponent as LegislatorIcon } from '../assets/person.svg';

function App() {
  return (
    <Router>
      <div className={styles.container}>
        <div className={styles.leftNavBackground} />
        <div className={styles.appTitle}>
          <h1>350 Brooklyn</h1>
          <h2>Bill Tracker</h2>
        </div>
        <Link to="/" className={styles.billsLogo}>
          <BillsIcon />
        </Link>
        <Link to="/" className={styles.billsLink}>
          Bills
        </Link>
        <Link to="/council-members" className={styles.legislatorsLogo}>
          <LegislatorIcon />
        </Link>
        <Link to="/council-members" className={styles.legislatorsLink}>
          Council members
        </Link>
        <Link to="/setting" className={styles.settingsLogo}>
          <SettingsIcon />
        </Link>
        <Link to="/settings" className={styles.settingsLink}>
          Settings
        </Link>
        <Link to="/logout" className={styles.logoutLogo}>
          <LogoutIcon />
        </Link>
        <Link to="/settings" className={styles.logoutLink}>
          Logout
        </Link>
        <main className={styles.content}>
          <Route path="/" exact>
            <Redirect to="/saved-bills" />
          </Route>
          <Route
            path="/saved-bills/:billId?"
            exact
            component={BillsPage}
          />
          <Route
            path="/council-members/:legislatorId?"
            component={LegislatorsPage}
          />
        </main>
      </div>
    </Router>
  );
}

export default App;
