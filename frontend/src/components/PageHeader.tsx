import React, { ReactElement } from 'react';
import styles from '../style/components/PageHeader.module.scss';

interface Props {
    children: string | ReactElement;
}

export default function PageHeader(props: Props) {
    return <h1 className={styles.title}>{props.children}</h1>;
}