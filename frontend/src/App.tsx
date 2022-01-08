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
import Dossier, { DossierPerson } from './Dossier';
import Adams from './assets/adams.png';
import Justin from './assets/justin.png'


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
  const dossierPerson: DossierPerson = {
    name: "Adrienne Adams",
    district: 28,
    borough: "Queens",
    neighborhoods: "Jamaica, Richmond Hill, Rochdale Village, South Ozone Park",
    party: "Democrat",
    twitter: "CMAdrienneAdams",
    title: "Speaker",
    bio: "Before helming Community Board 12 and being elected CM was a former Corporate Trainer who worked in Human Capital Management at several Fortune 500 corporations, specializing in Executive Training and Telecom Management. Served as a Child Development Associate Instructor, training child care professionals.",
    priorities: "Seeing the city through the pandemic and working to strengthen families that have been damaged in its wake.",
    otherNotes: "Strong education focus. Attended same high school as Mayor Adams. An AKA. Attended Spelman as did CM Hudson.",
    quote: "“All roads lead through this pandemic,” she said. “When I think of my priorities, I think of rebuilding a city.” ",
    email: "AEAdams@council.nyc.gov",
    image: Adams,
  }
  const justin = {
    name: "Justin Brannan",
    district: 43,
    borough: "Brooklyn",
    neighborhoods: "Bay Ridge",
    party: "Democrat",
    twitter: "JustinBrannan",
    title: "Guitarist",
    bio: 'Before entering politics, Justin Brannan was a hardcore punk guitarist for the bands Indecision from 1993 to 2000 and Most Precious Blood from 2000 onwards. Both bands were known for their outspoken commitment to social justice and vegetarianism. Indecision is widely known for their song "Hallowed be Thy Name". The song features a lyric ("For Those I Love I Will Sacrifice") wrote by Brannan when he was sixteen years old that fans across the world have turned into a tattoo.',
    priorities: "Public schools, homelessness, protecting new immigrants, the opioid epidemic, and income inequality.",
    otherNotes: "Brannan also founded the deathgrind band Caninus, known for using two dogs as vocalists.",
    quote: "“Who should I die for, who will collapse me, FOR THOSE I LOVE I WILL SACRIFICE, Hallowed be thy name”",
    email: "JustinBrannan@council.nyc.gov",
    image: Justin
  }
  return <div><Dossier dossierPerson={dossierPerson}/><Dossier dossierPerson={justin} /></div>
  // return (
  //   <AuthContextProvider>
  //     <Router>
  //       <AppContent />
  //     </Router>
  //   </AuthContextProvider>
  // );
}

export default App;
