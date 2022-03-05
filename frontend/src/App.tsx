import './style/App.scss';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import BillListPage from './pages/BillListPage';
import PersonsPage from './pages/PersonsPage';
import styles from './style/App.module.scss';
import React, { useContext, useState } from 'react';
import RequestLoginLinkPage from './pages/RequestLoginLinkPage';
import { AuthContextProvider, AuthContext } from './AuthContext';
import { useLocation } from 'react-router-dom';
import LoginFromTokenPage from './pages/LoginFromTokenPage';
import SettingsPage from './pages/SettingsPage';
import BillDetailsPage from './pages/BillDetailsPage';
import LeftNav from './components/LeftNav';
import { setSyntheticLeadingComments } from 'typescript';
import MobileHeader from './components/MobileHeader';

function AppContent() {
  const authContext = useContext(AuthContext);

  const [mobileMenuShown, setMobileMenuShown] = useState<boolean>(false);

  const location = useLocation();

  if (location.pathname === '/login') {
    return <LoginFromTokenPage />;
  }

  if (!authContext.token) {
    return <RequestLoginLinkPage errorCode={location.hash.substring(1)}/>;
  }

  function handleLogout(event: any) {
    event.preventDefault();
    authContext.updateToken(null);
    window.location.replace('/');
  }

  function handleMobileMenuIconClicked() {
    setMobileMenuShown(true);
  }

  function handleMobileMenuCloseClicked() {
    setMobileMenuShown(false);
  }

  const leftNavClassNames = [styles.leftNav];
  if (mobileMenuShown) {
    leftNavClassNames.push(styles.leftNavMobileShown);
  }
  return (
    <Router>
      <div className={styles.pageContainer}>
        <MobileHeader onMenuClicked={handleMobileMenuIconClicked} />
        <div className={leftNavClassNames.join(" ")}>
          <LeftNav onLogout={handleLogout} onMobileMenuClosed={handleMobileMenuCloseClicked} />
        </div>

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
  return (
    <AuthContextProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthContextProvider>
  );
}

export default App;
