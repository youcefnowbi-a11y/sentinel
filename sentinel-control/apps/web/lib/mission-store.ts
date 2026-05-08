import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import type {
  EscalationRequestRow,
  MissionActionRow,
  MissionArtifactRow,
  MissionRecord,
  MissionStateRow,
  MissionStatus,
  MissionTraceEventRow,
  MissionTypeRow,
} from "@/lib/types";

type MissionStateFile = {
  version: 1;
  missions: MissionRecord[];
};

const STORE_PATH = path.resolve(process.cwd(), "../../data/mission_state.json");
const createdAt = "2026-04-26T10:00:00.000Z";

export const missionTypes: MissionTypeRow[] = [
  {
    id: "gtm",
    label: "GTM Mission",
    description: "Creates a bounded first-customer GTM pack with drafts, watchlist, roadmap, trace, and review gates.",
    status: "enabled",
    allowedActions: [
      "create_project_folder",
      "generate_gtm_pack",
      "generate_landing_copy",
      "generate_outreach_drafts_without_sending",
      "create_watchlist",
      "generate_research_questions",
      "write_trace",
    ],
    allowedTools: ["safe_file_writer"],
    blackZoneActions: ["run_shell_command", "browser_submit_form", "desktop_control", "payment", "credential_access", "production_mutation"],
  },
  {
    id: "research_summary",
    label: "Research Summary Mission",
    description: "A lab-only non-GTM mission type proving that the Mission OS can run more than one agent family.",
    status: "lab_only",
    allowedActions: ["create_project_folder", "create_markdown_file", "write_trace"],
    allowedTools: ["safe_file_writer"],
    blackZoneActions: ["run_shell_command", "browser_submit_form", "desktop_control", "payment", "credential_access", "production_mutation"],
  },
];

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function missionState(missionId: string, status: MissionStatus, currentStep: string, actionCount: number): MissionStateRow {
  return {
    missionId,
    status,
    currentStep,
    actionCount,
    costUsed: 0.12,
    startedAt: createdAt,
    updatedAt: createdAt,
    endedAt: status === "completed" ? "2026-04-26T10:05:00.000Z" : undefined,
  };
}

function trace(id: string, missionId: string, eventType: string, summary: string, actionId?: string): MissionTraceEventRow {
  return {
    id,
    missionId,
    eventType,
    actor: eventType.startsWith("user_") ? "user" : "sentinel",
    actionId,
    summary,
    reversible: true,
    cost: 0,
    timestamp: createdAt,
  };
}

function action(id: string, missionId: string, actionType: string, route: MissionActionRow["route"], riskScore: number): MissionActionRow {
  return {
    id,
    missionId,
    actionType,
    tool: "safe_file_writer",
    intent: actionType.replace(/_/g, " "),
    target: `data/generated_projects/${missionId}`,
    expectedOutput: "Local artifact generated under mission workspace.",
    reversibility: actionType.includes("draft") ? "draft" : "local_write_reversible",
    externality: "internal_local",
    sensitivity: "internal",
    estimatedCost: 0,
    confidence: "high",
    riskScore,
    route,
    evidenceRefs: ["ev_direct", "ev_wtp"],
    createdAt,
    executedAt: route === "auto_execute" || route === "log_and_continue" ? createdAt : undefined,
  };
}

function artifact(id: string, missionId: string, artifactType: string, filePath: string, actionId: string): MissionArtifactRow {
  return {
    id,
    missionId,
    artifactType,
    path: filePath,
    evidenceRefs: ["ev_direct", "ev_wtp"],
    status: "created",
    createdByActionId: actionId,
    canRollback: true,
    createdAt,
  };
}

function seedMissions(): MissionRecord[] {
  const gtmId = "mission_gtm_launch_pack";
  const researchId = "mission_research_summary";
  const gtmActions = [
    action("mact_workspace", gtmId, "create_project_folder", "auto_execute", 0),
    action("mact_pack", gtmId, "generate_gtm_pack", "auto_execute", 0),
    action("mact_outreach", gtmId, "generate_outreach_drafts_without_sending", "log_and_continue", 15),
    action("mact_shell", gtmId, "run_shell_command", "block", 100),
  ];
  const researchActions = [
    action("mact_research_workspace", researchId, "create_project_folder", "auto_execute", 0),
    action("mact_research_summary", researchId, "create_markdown_file", "auto_execute", 0),
  ];

  return [
    {
      missionType: missionTypes[0],
      envelope: {
        id: gtmId,
        userId: "local_user",
        missionType: "gtm",
        missionTitle: "Create Sentinel GTM launch pack",
        missionObjective: "Generate a local first-customer GTM pack with outreach drafts and watchlist.",
        successCriteria: ["GTM files exist", "Outreach remains draft-only", "Mission timeline exists", "ReviewerLite passes"],
        mode: "operator",
        allowedSystems: ["local_workspace", "cueidea_import"],
        allowedTools: ["safe_file_writer"],
        allowedActions: missionTypes[0].allowedActions,
        forbiddenActions: missionTypes[0].blackZoneActions,
        allowedPaths: ["data/generated_projects"],
        allowedDomains: [],
        allowedAccounts: [],
        allowedDataTypes: ["public_market_evidence", "internal_project_context"],
        maxDurationMinutes: 60,
        maxActions: 20,
        maxCostUsd: 2,
        maxRecipients: 0,
        riskAppetiteScore: 35,
        escalationTriggers: ["external", "irreversible", "sensitive", "out_of_scope", "low_confidence"],
        rollbackPreference: "metadata_only",
        traceLevel: "standard",
        emergencyStopEnabled: true,
        createdAt,
        expiresAt: "2026-04-26T11:00:00.000Z",
      },
      state: missionState(gtmId, "completed", "mission_completed", 3),
      actions: gtmActions,
      artifacts: [
        artifact("mart_verdict", gtmId, "gtm_verdict", "00_VERDICT.md", "mact_pack"),
        artifact("mart_icp", gtmId, "icp", "02_ICP.md", "mact_pack"),
        artifact("mart_outreach", gtmId, "outreach_drafts", "05_OUTREACH_MESSAGES.md", "mact_outreach"),
        artifact("mart_watchlist", gtmId, "watchlist", "08_WATCHLIST.md", "mact_pack"),
      ],
      traceEvents: [
        trace("mev_created", gtmId, "mission_created", "Mission authority envelope accepted."),
        trace("mev_started", gtmId, "mission_started", "Mission started inside authorized scope."),
        trace("mev_pack", gtmId, "action_executed", "Generated GTM pack files.", "mact_pack"),
        trace("mev_blocked", gtmId, "action_blocked", "Shell command blocked even inside operator mode.", "mact_shell"),
        trace("mev_review", gtmId, "review_executed", "ReviewerLite checked mission artifacts before completion."),
        trace("mev_completed", gtmId, "mission_completed", "Mission completed after success evaluation."),
      ],
      escalations: [],
      reviewer: { ready: true, issues: [] },
    },
    {
      missionType: missionTypes[1],
      envelope: {
        id: researchId,
        userId: "local_user",
        missionType: "research_summary",
        missionTitle: "Summarize Mission OS extensibility",
        missionObjective: "Create one research summary artifact through the same generic runner.",
        successCriteria: ["Research summary exists", "Timeline exists", "Artifact index exists"],
        mode: "safe",
        allowedSystems: ["local_workspace"],
        allowedTools: ["safe_file_writer"],
        allowedActions: missionTypes[1].allowedActions,
        forbiddenActions: missionTypes[1].blackZoneActions,
        allowedPaths: ["data/generated_projects"],
        allowedDomains: [],
        allowedAccounts: [],
        allowedDataTypes: ["public_project_context"],
        maxDurationMinutes: 20,
        maxActions: 5,
        maxCostUsd: 0.25,
        maxRecipients: 0,
        riskAppetiteScore: 20,
        escalationTriggers: ["out_of_scope", "sensitive"],
        rollbackPreference: "metadata_only",
        traceLevel: "standard",
        emergencyStopEnabled: true,
        createdAt,
        expiresAt: "2026-04-26T10:20:00.000Z",
      },
      state: missionState(researchId, "completed", "mission_completed", 2),
      actions: researchActions,
      artifacts: [artifact("mart_research", researchId, "research_summary", "RESEARCH_SUMMARY.md", "mact_research_summary")],
      traceEvents: [
        trace("mev_research_created", researchId, "mission_created", "Research mission envelope accepted."),
        trace("mev_research_summary", researchId, "action_executed", "Research summary file created.", "mact_research_summary"),
        trace("mev_research_completed", researchId, "mission_completed", "Research summary mission completed through generic runner."),
      ],
      escalations: [],
      reviewer: { ready: true, issues: [] },
    },
  ];
}

async function readState(): Promise<MissionStateFile> {
  try {
    const raw = await readFile(STORE_PATH, "utf8");
    const parsed = JSON.parse(raw) as MissionStateFile;
    if (parsed.version === 1 && Array.isArray(parsed.missions)) {
      return parsed;
    }
  } catch {
    // Local mission state is initialized lazily for the dashboard.
  }
  const state: MissionStateFile = { version: 1, missions: seedMissions() };
  await writeState(state);
  return state;
}

async function writeState(state: MissionStateFile) {
  await mkdir(path.dirname(STORE_PATH), { recursive: true });
  await writeFile(STORE_PATH, `${JSON.stringify(state, null, 2)}\n`, "utf8");
}

export async function listMissions() {
  const state = await readState();
  return clone(state.missions);
}

export async function getMission(missionId: string) {
  const state = await readState();
  const mission = state.missions.find((item) => item.envelope.id === missionId);
  return mission ? clone(mission) : null;
}

export async function updateMissionStatus(missionId: string, status: Extract<MissionStatus, "paused" | "stopped" | "revoked">) {
  const state = await readState();
  const mission = state.missions.find((item) => item.envelope.id === missionId);
  if (!mission) return null;

  const updatedAt = new Date().toISOString();
  mission.state.status = status;
  mission.state.updatedAt = updatedAt;
  if (status === "revoked") {
    mission.envelope.revokedAt = updatedAt;
  }
  if (status === "stopped" || status === "revoked") {
    mission.state.endedAt = updatedAt;
  }

  mission.traceEvents = [
    {
      id: `mev_${status}_${Date.now()}`,
      missionId,
      eventType: `mission_${status}`,
      actor: "user",
      summary: `User selected ${status} from Mission Control.`,
      reversible: status === "paused",
      cost: 0,
      timestamp: updatedAt,
    },
    ...mission.traceEvents,
  ];

  await writeState(state);
  return clone(mission);
}
