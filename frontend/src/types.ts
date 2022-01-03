// Defines types returned by the backend APIs.

export type Uuid = string;

export type BillType = 'CITY' | 'STATE';
export type StateChamber = 'SENATE' | 'ASSEMBLY';

export interface CityBill {
  status: string;
  file: string;
  cityBillId: number;
  councilBody: string; // this is the committee name
  sponsorCount: number; // TODO: implement on backend
}

export interface StateChamberBill {
  basePrintNo: string;
  activeVersionName: string; // rename to active_version
  status: string;
  sponsorCount: number; // TODO: implement on backend
  senateWebsite: string;
  assemblyWebsite: string;
}

export interface StateBill {
  sessionYear: number;
  summary: string;
  senateBill: StateChamberBill | null;
  assemblyBill: StateChamberBill | null;
}

export interface StateBillSponsorships {
  billId: string;
  senateSponsors: Person[];
  senateNonSponsors: Person[];
  assemblySponsors: Person[];
  assemblyNonSponsors: Person[];
}

export interface StateBillSearchResult {
  name: string;
  description: string;
  status: string;
  basePrintNo: string;
  sessionYear: number;
  chamber: StateChamber;
  activeVersion: string;
  tracked: boolean;
}

export interface Bill {
  // Non-editable fields
  id: string;
  name: string;
  description: string;
  tracked: boolean;
  codeName: string;
  status: string;

  // Editable fields
  notes: string;
  nickname: string;
  twitterSearchTerms: string[];

  type: BillType;
  cityBill: CityBill | null;
  stateBill: StateBill | null;
}

export type PersonType = 'COUNCIL_MEMBER' | 'SENATOR' | 'ASSEMBLY_MEMBER' | 'STAFFER';

export interface CouncilMember {
  legislativePhone: string;
  borough: string;
  website: string;
  // ISO-formatted datetime.
  termStart: string;
  termEnd: string;
}

// TODO: Change types to reflect nullability
export interface Person {
  id: string;
  name: string;
  title: string;
  email: string;
  phone: string;
  twitter: string;
  party: string;

  // Editable data
  notes: string;
  type: PersonType;
  councilMember: CouncilMember | null;
}

export interface SingleMemberSponsorship {
  bill: Bill;
  personId: string;
}

export interface CitySponsorship {
  billId: string;
  person: Person;
  isSponsor: boolean;
  sponsorSequence: number | null;
}

export interface BillAttachment {
  id: number;
  billId: number;
  url: string;
  name: string;
  status: string;
}

export interface PowerHour {
  id: number;
  billId: number;
  spreadsheetUrl: string;
  title: string;
  createdAt: string; // ISO DateTime
}

export interface CreatePowerHourResponse {
  messages: string[];
  powerHour: PowerHour;
}

export interface User {
  id: Uuid;
  name: string;
  email: string;
  canBeDeleted: boolean;
  sendBillUpdateNotifications: boolean;
}

export interface Staffer {
  id: Uuid;
  name: string;
  title: string;
  email: string;
  phone: string;
  twitter: string;
}
