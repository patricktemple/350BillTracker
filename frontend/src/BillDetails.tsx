import React, { ReactElement } from 'react';
import Stack from 'react-bootstrap/Stack';
import { Bill } from './types';

interface Props {
  bill: Bill;
}

export default function BillDetails(props: Props): ReactElement {
  const { bill } = props;
  return (
    <Stack direction="vertical" gap={2}>
      <div>
        <strong>File:</strong> {bill.file}
      </div>
      <div>
        <strong>Title:</strong> {bill.title}
      </div>
      <div>
        <strong>Name:</strong> {bill.name}
      </div>
    </Stack>
  );
}