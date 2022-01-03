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
}

export interface StateBill {
  sessionYear: number;
  summary: string;
  senateBill: StateChamberBill | null;
  assemblyBill: StateChamberBill | null;
}

// class StateBillSearchResultSchema(CamelCaseSchema):
//     name = fields.String(dump_only=True)
//     description = fields.String(dump_only=True)
//     status = fields.String(dump_only=True)
//     base_print_no = fields.String(dump_only=True)
//     session_year = fields.String(dump_only=True)
//     chamber = EnumField(StateChamber, dump_only=True)
//     active_version = fields.String(dump_only=True)
//     tracked = fields.Boolean(dump_only=True)
//     other_chamber_bill_print_no = fields.String(dump_only=True)

export interface StateBillSearchResult {
  name: string;
  description: string;
  status: string;
  basePrintNo: string;
  sessionYear: string; // number?
  chamber: StateChamber;
  activeVersion: string;
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

export type PersonType = 'COUNCIL_MEMBER' | 'SENATOR' | 'ASSEMBLY_MEMBER';

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
  sponsorSequence: number;
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
