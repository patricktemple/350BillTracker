import './style/App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import BillListPage from './BillListPage';
import PersonsPage from './PersonsPage';
import styles from './style/App.module.scss';
import { Link } from 'react-router-dom';
import { ReactComponent as SettingsIcon } from './assets/settings.svg';
import { ReactComponent as LogoutIcon } from './assets/logout.svg';
import { ReactComponent as BillsIcon } from './assets/paper.svg';
import { ReactComponent as LegislatorIcon } from './assets/person.svg';
import React, { useContext } from 'react';
import RequestLoginLinkPage from './RequestLoginLinkPage';
import { AuthContextProvider, AuthContext } from './AuthContext';
import { useLocation } from 'react-router-dom';
import LoginFromTokenPage from './LoginFromTokenPage';
import SettingsPage from './SettingsPage';
import BillDetailsPage from './BillDetailsPage';
import Dossier from './Dossier';

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
        <Link to="/people" className={styles.legislatorsLogo}>
          <LegislatorIcon />
        </Link>
        <Link to="/people" className={styles.legislatorsLink}>
          People
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
          <Route exact path="/">
            <Redirect to="/bills" />
          </Route>
          <Route exact path="/bills" component={BillListPage} />
          <Route path="/bills/:billId" component={BillDetailsPage} />
          <Route path="/people/:personId?" component={PersonsPage} />
          <Route path="/settings" component={SettingsPage} />
        </main>
      </div>
    </Router>
  );
}

function App() {
  return <Dossier />;
  // return (
  //   <AuthContextProvider>
  //     <Router>
  //       <AppContent />
  //     </Router>
  //   </AuthContextProvider>
  // );
}

export default App;
