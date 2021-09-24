// Types returned by backend API. snake_case because that's what python does naturally?
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

  // Or date?
  term_start: string;
  term_end: string;
}
