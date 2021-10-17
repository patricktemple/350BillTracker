import './style/App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import BillsPage from './BillsPage';
import LegislatorsPage from './LegislatorsPage';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import styles from './style/App.module.scss';
import { Link } from 'react-router-dom';
import { ReactComponent as SettingsIcon } from './assets/settings.svg';
import { ReactComponent as LogoutIcon } from './assets/logout.svg';
import { ReactComponent as BillsIcon } from './assets/paper.svg';
import { ReactComponent as LegislatorIcon } from './assets/person.svg';
import React, { useState, useContext } from 'react';
import { MdPeople, MdDescription } from 'react-icons/md';
import RequestLoginLinkPage from './RequestLoginLinkPage';
import { AuthContextProvider, AuthContext } from './AuthContext';
import { useLocation } from 'react-router-dom';
import LoginFromTokenPage from './LoginFromTokenPage';
import Button from 'react-bootstrap/Button';
import SettingsPage from './SettingsPage';
import TwitterList from './TwitterList';

function AppContent() {
  const authContext = useContext(AuthContext);

  const location = useLocation();

  if (location.pathname === '/login') {
    return <LoginFromTokenPage />;
  }

  if (!authContext.token) {
    return <RequestLoginLinkPage />;
  }

  function handleLogout(event: any) {
    event.preventDefault();
    authContext.updateToken(null);
    window.location.replace('/');
  }

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
        <a href="#" onClick={handleLogout} className={styles.logoutLogo}>
          <LogoutIcon />
        </a>
        <a href="#" onClick={handleLogout} className={styles.logoutLink}>
          Logout
        </a>
        <main className={styles.content}>
          <Route path="/twitter" component={TwitterList} />
          <Route path="/" exact>
            <Redirect to="/saved-bills" />
          </Route>
          <Route path="/saved-bills/:billId?" exact component={BillsPage} />
          <Route
            path="/council-members/:legislatorId?"
            component={LegislatorsPage}
          />
          <Route path="/settings" component={SettingsPage} />
        </main>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthContextProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthContextProvider>
  );
}

export default App;
