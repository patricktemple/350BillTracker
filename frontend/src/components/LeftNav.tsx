import { Link } from 'react-router-dom';
import { ReactComponent as SettingsIcon } from '../assets/settings.svg';
import { ReactComponent as LogoutIcon } from '../assets/logout.svg';
import { ReactComponent as BillsIcon } from '../assets/paper.svg';
import { ReactComponent as PersonIcon } from '../assets/person.svg';
import AppLogo from '../assets/app-logo.png';
import React from 'react';

import styles from '../style/components/LeftNav.module.scss';

export interface Props {
    onLogout: (event: any) => void;
}

export default function LeftNav(props: Props) {
    return (
            <div className={styles.container}>
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
            </div>
    );
}