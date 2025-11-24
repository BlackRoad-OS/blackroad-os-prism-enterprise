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
import { Decimal } from "decimal.js";

export type EntitlementStatus = "Active" | "Revoked" | "Expired";
export type SodConstraint =
  | "MUTUAL_EXCLUSION"
  | "APPROVER_CANNOT_EXECUTE"
  | "FOUR_EYES";
export type SodConflictStatus =
  | "Open"
  | "ApprovedException"
  | "Mitigated"
  | "Resolved";
export type RfcType = "CODE" | "POLICY" | "INFRA" | "CONTENT";
export type RfcStatus =
  | "Draft"
  | "InReview"
  | "Approved"
  | "Rejected"
  | "Implemented"
  | "Failed"
  | "RolledBack";
export type VendorCategory =
  | "Custodian"
  | "CryptoVenue"
  | "Data"
  | "Cloud"
  | "Advisory"
  | "Other";
export type VendorCriticality = "High" | "Medium" | "Low";
export type VendorStatus = "Active" | "Onboarding" | "Offboarded";
export type VendorDocKind =
  | "MSA"
  | "BAA"
  | "SOC2"
  | "ISO"
  | "PenTest"
  | "Insurance"
  | "Financials"
  | "BCP"
  | "Privacy";
export type DdqStatus = "Pending" | "Completed" | "Expired";
export type IncidentType =
  | "Security"
  | "Privacy"
  | "Ops"
  | "Vendor"
  | "BCP";
export type IncidentSeverity = "SEV1" | "SEV2" | "SEV3" | "SEV4";
export type IncidentStatus =
  | "Open"
  | "Mitigated"
  | "Resolved"
  | "Closed";
export type BcpStatus = "Active" | "Draft";

export interface User {
  id: string;
  name: string;
  email: string;
}

export interface Role {
  id: string;
  key: string;
  title: string;
}

export interface Permission {
  id: string;
  key: string;
  desc: string;
}

export interface RolePermission {
  id: string;
  roleId: string;
  permissionId: string;
}

export interface Entitlement {
  id: string;
  userId: string;
  roleId: string;
  grantedBy: string;
  grantedAt: Date;
  expiresAt?: Date | null;
  status: EntitlementStatus;
  recertDue?: Date | null;
}

export interface SodRule {
  id: string;
  key: string;
  description: string;
  constraint: SodConstraint;
  leftRole: string;
  rightRole?: string | null;
  scope?: string | null;
  severity: number;
}

export interface SodConflict {
  id: string;
  userId: string;
  ruleKey: string;
  status: SodConflictStatus;
  createdAt: Date;
  resolvedAt?: Date | null;
  notes?: string | null;
}

export interface Rfc {
  id: string;
  title: string;
  type: RfcType;
  description: string;
  riskScore: number;
  status: RfcStatus;
  requesterId: string;
  approverIds: string[];
  submittedAt?: Date | null;
  decidedAt?: Date | null;
  implementedAt?: Date | null;
  rollbackPlan?: string | null;
  postImplReview?: unknown;
  links: unknown;
  notes?: string | null;
}

export interface Vendor {
  id: string;
  name: string;
  category: VendorCategory;
  criticality: VendorCriticality;
  status: VendorStatus;
  riskScore: number;
  nextReview?: Date | null;
}

export interface VendorDoc {
  id: string;
  vendorId: string;
  kind: VendorDocKind;
  path: string;
  sha256: string;
  expiresAt?: Date | null;
  receivedAt: Date;
}

export interface Ddq {
  id: string;
  vendorId: string;
  questionnaireKey: string;
  answers: unknown;
  score: number;
  status: DdqStatus;
  completedAt?: Date | null;
}

export interface Incident {
  id: string;
  title: string;
  type: IncidentType;
  severity: IncidentSeverity;
  status: IncidentStatus;
  detectedAt: Date;
  acknowledgedAt?: Date | null;
  resolvedAt?: Date | null;
  description: string;
  rootCause?: string | null;
  correctiveActions?: string | null;
  communications: unknown;
  relatedIds: unknown;
}

export interface BcpPlan {
  id: string;
  version: number;
  effectiveAt: Date;
  rtoMinutes: number;
  rpoMinutes: number;
  contacts: unknown;
  scenarios: unknown;
  tests: unknown;
  status: BcpStatus;
}

export interface BcpTestRecord {
  id: string;
  planId: string;
  runAt: Date;
  scenario: string;
  participants: string[];
  issues: string[];
  outcome: "Pass" | "Fail" | "NeedsFollowup";
}

export interface Kri {
  id: string;
  key: string;
  label: string;
  value: Decimal;
  asOf: Date;
  meta: unknown;
}

export interface GateDecision {
  action: string;
  allowed: boolean;
  reason?: string;
  context?: Record<string, unknown>;
  evaluatedAt: Date;
}

export interface PolicyContext {
  sodSeverityThreshold: number;
  recertGraceDays: number;
  vendorCriticalRiskThreshold: number;
  defaultRecertIntervalDays: number;
  bcPlanTestCadenceDays: number;
  privacyNotificationHours: number;
  fourEyesActions: Set<string>;
}

export interface FourEyesApproval {
  action: string;
  preparerId: string;
  approverIds: string[];
export interface Identity {
  id: string;
  publicKey: string;
  settings: Record<string, unknown>;
export type TrackType = "securities" | "insurance" | "real_estate";

export type LicenseStatus = "Active" | "Expired" | "Lapsed" | "Barred" | "Unknown";

export type TaskStatus = "Open" | "Done" | "Blocked" | "N/A";

export type FilingArtifactKind =
  | "Form"
  | "ProofCE"
  | "Fee"
  | "Fingerprint"
  | "Background"
  | "Appointment"
  | "Bond"
  | "Affidavit"
  | "ExamPass";

export interface PersonPriorEmployer {
  name: string;
  role?: string;
}

export interface Person {
  id: string;
  legalName: string;
  aka: string[];
  crdNumber?: string;
  homeState: string;
  tracks: TrackType[];
  targetStates: string[];
  disclosures: string[];
  designations: string[];
  priorEmployers: PersonPriorEmployer[];
}

export interface LicenseTrack {
  id: string;
  personId: string;
  track: TrackType;
  stateCode: string;
  licenseType: string;
  status: LicenseStatus;
  number?: string;
  lastRenewal?: Date;
  expiration?: Date;
  ceHoursEarned?: number;
  ceHoursRequired?: number;
  notes?: string;
  metadata?: Record<string, unknown> | null;
}

export interface Rulebook {
  id: string;
  stateCode: string;
  track: TrackType;
  licenseType: string;
  version: number;
  sourceUrls: string[];
  rules: ReinstatementRule;
}

export type TransitionFrom = "Expired" | "Lapsed" | "Unknown";
export type TransitionTo = "Active" | "Requalify";

export interface TransitionRule {
  from: TransitionFrom;
  to: TransitionTo;
  conditions: string[];
  tasks: TaskTemplateKey[];
}

export interface ReinstatementRule {
  graceWindowDays?: number;
  reinstatementWindowDays?: number;
  requiresExamRetakeIfBeyondDays?: number;
  requiresPrelicensingIfBeyondDays?: number;
  ce: {
    requiredHours: number;
    ethicsHours?: number;
    carryover?: boolean;
  } | null;
  backgroundCheck: {
    fingerprints: boolean;
  } | null;
  sponsorRequired: boolean;
  formSet: FormKey[];
  fees: {
    renewal?: number;
    reinstatementPenalty?: number;
    exam?: number;
  } | null;
  appointmentsResetOnReinstatement?: boolean;
  docsNeeded: DocKey[];
  transitions: TransitionRule[];
}

export type FormKey = "U4" | "U5" | "ADV" | "StateApp" | "NIPR" | "Sircon" | "RealEstateApp";

export type DocKey = "PhotoID" | "ResidentProof" | "ExamPass" | "CECert" | "Bond" | "Affidavit";

export type TaskTemplateKey =
  | "FETCH_CRD_HISTORY"
  | "PARSE_BROKERCHECK_PDF"
  | "VERIFY_DISCLOSURES"
  | "SCHEDULE_SERIES65_EXAM"
  | "FILE_U4"
  | "ADV_FILE_FIRM"
  | "INSURANCE_REINSTATE_VIA_SIRCON"
  | "UPLOAD_CE_CERTS"
  | "PAY_REINSTATEMENT_FEE"
  | "REAL_ESTATE_REINSTATE"
  | "FINGERPRINTS"
  | "APPOINTMENTS_REAPPLY"
  | "SECURE_BD_SPONSOR"
  | "VERIFY_LICENSE_EXPIRATION"
  | "COMPLETE_BACKGROUND_CHECK"
  | "SUBMIT_STATE_APPLICATION"
  | "PAY_STATE_FEES"
  | "PRELICENSING_COURSE"
  | "SCHEDULE_INSURANCE_EXAM"
  | "NEW_APPLICATION"
  | "SCHEDULE_REAL_ESTATE_EXAM";

export interface TaskTemplate {
  key: TaskTemplateKey;
  title: string;
  description: string;
  blocking: boolean;
  defaultDueInDays?: number;
  requiredArtifacts: FilingArtifactKind[];
}

export interface PlannedTask {
  id: string;
  personId: string;
  stateCode: string;
  track: TrackType;
  licenseType: string;
  template: TaskTemplateKey;
  title: string;
  status: TaskStatus;
  blocking: boolean;
  due?: Date | null;
  payload?: Record<string, unknown>;
  requiredArtifacts: FilingArtifactKind[];
}

export interface RuleEvaluationResult {
  target: TransitionTo;
  tasks: PlannedTask[];
  blockers: string[];
  fees: {
    renewal?: number;
    reinstatementPenalty?: number;
    exam?: number;
  } | null;
  notes: string[];
}

export interface PlanOptions {
  targetStates: string[];
  targetTracks: TrackType[];
  now?: Date;
}

export interface PlannerResult {
  tasks: PlannedTask[];
  summaries: PlanSummary[];
}

export interface PlanSummary {
  stateCode: string;
  track: TrackType;
  licenseType: string;
  targetStatus: TransitionTo;
  blockers: string[];
  fees: {
    renewal?: number;
    reinstatementPenalty?: number;
    exam?: number;
  } | null;
  tasks: PlannedTask[];
}

export interface GateResult {
  allowed: boolean;
  reason?: string;
}

export interface TaskCompletionPayload {
  taskId: string;
  artifacts: Array<{ kind: FilingArtifactKind; path: string }>;
}
