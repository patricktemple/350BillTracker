import React from 'react';
import styles from '../style/components/MobileHeader.module.scss';
import AppLogo from '../assets/app-logo.png';

import { ReactComponent as HamburgerIcon } from '../assets/hamburger.svg';

interface Props {
    onMenuClicked: () => void;
}

export default function MobileHeader(props: Props) {
    // Should make the shole div an A tag? Read up on best practice here
    return (
        <div className={styles.container}>
            <img src={AppLogo} alt="Logo" />
            <span className={styles.appTitle}>Bill tracker</span>

            <div className={styles.menuContainer} onClick={props.onMenuClicked}>
                Menu
               <HamburgerIcon />
            </div>
        </div>
    );
}