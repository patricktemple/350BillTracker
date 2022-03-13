import React, { ReactElement } from 'react';
import styles from '../style/components/DetailTable.module.scss';

export interface Props {
  children: any;
}

export function DetailLabel(props: { children: any }) {
  return <div className={styles.label}>{props.children}</div>;
}

export function DetailContent(props: { children: any }) {
  return <div className={styles.content}>{props.children}</div>;
}

export default function DetailTable(props: Props) {
  return <div className={styles.container}>{props.children}</div>;
}
