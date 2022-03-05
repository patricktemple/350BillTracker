import { Link } from 'react-router-dom';
import { ReactComponent as SettingsIcon } from '../assets/settings.svg';
import { ReactComponent as LogoutIcon } from '../assets/logout.svg';
import { ReactComponent as BillsIcon } from '../assets/paper.svg';
import { ReactComponent as PersonIcon } from '../assets/person.svg';
import AppLogo from '../assets/app-logo.png';
import React from 'react';

import { ReactComponent as CloseIcon } from '../assets/close-menu.svg';

import styles from '../style/components/LeftNav.module.scss';

export interface Props {
  onLogout: (event: any) => void;
  onMobileMenuClosed: () => void;
}

export default function LeftNav(props: Props) {
  // Again, see if an A tag is better for onclick on close icon
  // TODO: Also hide this when someone clicks any of the pages
  return (
    <nav className={styles.container}>
      <CloseIcon className={styles.mobileCloseIcon} onClick={props.onMobileMenuClosed} />
      <div className={styles.appTitle}>
        <img src={AppLogo} alt="Logo" className={styles.appLogo} />
        <h1>Bill Tracker</h1>
      </div>
      <div className={styles.mainLinkSection}>
        <Link to="/" className={styles.mainLinkItem}>
          <BillsIcon />
          Bills
        </Link>
        <Link to="/people" className={styles.mainLinkItem}>
          <PersonIcon />
          People
        </Link>
      </div>
      <div className={styles.bottomLinkSection}>
        <Link to="/settings" className={styles.bottomLinkItem}>
          <SettingsIcon /> Settings
        </Link>
        <a href="#" onClick={props.onLogout} className={styles.bottomLinkItem}>
          <LogoutIcon /> Log out
        </a>
      </div>
    </nav>
  );
}
