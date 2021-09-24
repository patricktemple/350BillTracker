// Defines types returned by the backend APIs.

export interface Bill {
  // Non-editable fields
  id: number;
  file: string;
  name: string;
  title: string;
  status: string;
  body: string;
  email: string;
  districtPhone: string;
  legislativePhone: string;
  tracked: boolean;

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
}
