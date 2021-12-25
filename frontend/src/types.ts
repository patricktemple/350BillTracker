// Defines types returned by the backend APIs.

export type Uuid = string;

export type BillType = "CITY" | "STATE";

export interface CityBill {
  title: string;
  status: string;
  file: string;
  cityBillId: number;
  councilBody: string; // this is the committee name
}

export interface Bill {
  // Non-editable fields
  id: string;
  name: string;
  tracked: boolean;

  // Editable fields
  notes: string;
  nickname: string;
  twitterSearchTerms: string[];

  type: BillType;
  cityBill: CityBill | null;
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

export interface BillSponsorship {
  billId: number;
  legislator: Legislator;
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
