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

  // Our data
  notes: string;
}

// TODO: This is stupid, just return the bill/member from the APIs alone
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
