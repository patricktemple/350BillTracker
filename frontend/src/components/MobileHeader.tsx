import React from 'react';
import styles from '../style/components/MobileHeader.module.scss';
import AppLogo from '../assets/app-logo.png';

import { ReactComponent as HamburgerIcon } from '../assets/hamburger.svg';
import { Link } from 'react-router-dom';

interface Props {
  onMenuClicked: () => void;
}

export default function MobileHeader(props: Props) {
  return (
    <div className={styles.container}>
      <Link to="/">
        <img src={AppLogo} alt="Logo" />
        <span className={styles.appTitle}>Bill tracker</span>
      </Link>

      <a className={styles.menuContainer} onClick={props.onMenuClicked}>
        Menu
        <HamburgerIcon />
      </a>
    </div>
  );
}
