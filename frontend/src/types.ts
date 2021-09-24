// Defines types returned by the backend APIs.

export interface Bill {
  id: number;
  file: string;
  name: string;
  title: string;
  status: string;
  body: string;
}

export interface CouncilMember {
  id: number;
  name: string;

  // ISO-formatted datetime.
  termStart: string;
  termEnd: string;
}
