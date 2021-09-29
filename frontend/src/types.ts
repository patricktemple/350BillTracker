// Defines types returned by the backend APIs.

export interface Bill {
  // Non-editable fields
  id: number;
  file: string;
  name: string;
  title: string;
  status: string;
  tracked: boolean;
  body: string;

  // Editable fields
  notes: string;
  nickname: string;
}

// TODO: Change types to reflect nullability
export interface Legislator {
  id: number;
  name: string;

  // ISO-formatted datetime.
  termStart: string;
  termEnd: string;
  email: string;
  districtPhone: string;
  legislativePhone: string;
  borough: string;
  website: string;
  twitter: string;
  party: string;

  // Editable data
  notes: string;
}

export interface SingleMemberSponsorship {
  bill: Bill;
  legislatorId: number;
}

export interface SingleBillSponsorship {
  billId: number;
  legislator: Legislator;
}

export interface BillAttachment {
  id: number;
  billId: number;
  url: string;
  name: string;
  status: string;
}
