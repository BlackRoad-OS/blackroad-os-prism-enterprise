export type Subject = "communication" | "client" | "employee" | "trade" | "vendor";

export interface EvalContext {
  state?: string;
  track?: string;
  date?: string;
}

export interface EvalInput<T = unknown> {
  subject: Subject;
  data: T;
  context: EvalContext;
}

export interface EvalResult {
  pass: boolean;
  riskScore: number;
  breaches: string[];
  requiredDisclosures?: string[];
  requiredEvidence?: string[];
  gateRecommendation?: "block" | "allow" | "review";
}

export interface PolicyEvaluator<T = unknown> {
  key: string;
  title: string;
  version: number;
  evaluate(input: EvalInput<T>): EvalResult;
}

export interface AttestationRequirement {
  policyKey: string;
  period: "Annual" | "Initial" | "AdHoc";
import type {
  AccountApp,
  AccountAppStatus,
  AccountChannel,
  AccountRiskTolerance,
  Business,
  Client,
  ClientRiskBand,
  ClientStatus,
  ClientType,
  Document,
  Gate,
  GateAction,
  Person,
  PersonRole,
  Screening,
  ScreeningStatus,
  ScreeningSubjectType,
  Wallet,
  WalletStatus,
} from "@blackroad/db";

export type {
  AccountApp,
  AccountAppStatus,
  AccountChannel,
  AccountRiskTolerance,
  Business,
  Client,
  ClientRiskBand,
  ClientStatus,
  ClientType,
  Document,
  Gate,
  GateAction,
  Person,
  PersonRole,
  Screening,
  ScreeningStatus,
  ScreeningSubjectType,
  Wallet,
  WalletStatus,
};

export interface SuitabilitySummary {
  score: number;
  band: ClientRiskBand;
  cryptoRiskBand?: "LOW" | "MODERATE" | "HIGH" | "SPECULATIVE";
  cryptoEligible?: boolean;
  cryptoBreaches?: string[];
  notes: string[];
  questionnaire: Record<string, unknown>;
}

export interface StartOnboardingInput {
  type: ClientType;
  channel: AccountChannel;
  accountType: string;
}

export interface StartOnboardingResult {
  client: Client;
  accountApp: AccountApp;
  checklist: string[];
}

export interface CreatePersonInput {
  clientId: string;
  role: PersonRole;
  name: string;
  emails?: string[];
  phones?: string[];
}

export interface CreateBusinessInput {
  clientId: string;
  legalName: string;
  formationCountry: string;
}

export interface SuitabilityInput {
  clientId: string;
  riskTolerance: AccountRiskTolerance;
  objectives: string[];
  timeHorizon: string;
  liquidityNeeds: string;
  experienceYears: number;
  crypto?: boolean;
  walletIds?: string[];
  questionnaire: Record<string, unknown>;
}

export interface DocGenerationInput {
  accountAppId: string;
  sets: string[];
}

export interface GateEvaluationResult {
  allowed: boolean;
  reason?: string;
}
