import React, { useState } from 'react';
import styles from '../style/components/SearchBox.module.scss';

interface Props {
  onChange: (text: string) => void;
  placeholder: string;
}

export default function SearchBox(props: Props) {
  const [text, setText] = useState<string>('');

  function handleChange(e: any) {
    setText(e.target.value);
    props.onChange(e.target.value);
  }

  return (
    <input
      type="text"
      placeholder={props.placeholder}
      value={text}
      className={styles.searchBox}
      size={30}
      onChange={handleChange}
    />
  );
}
