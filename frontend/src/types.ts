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

export interface CouncilMember {
  id: number;
  name: string;

  // ISO-formatted datetime.
  termStart: string;
  termEnd: string;
  email: string;
  districtPhone: string;
  legislativePhone: string;
}

export interface SingleBillSponsorship {
  billId: number;
  legislator: CouncilMember;
}