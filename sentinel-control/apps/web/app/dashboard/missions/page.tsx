import Link from "next/link";
import { ArrowUpRight, ShieldCheck } from "lucide-react";
import { Chip, Metric, SectionBand } from "@/components/ui";
import { listMissions } from "@/lib/mission-store";
import type { MissionStatus } from "@/lib/types";

export const dynamic = "force-dynamic";

function statusTone(status: MissionStatus): "neutral" | "good" | "warn" | "bad" {
  if (status === "completed") return "good";
  if (status === "failed" || status === "stopped" || status === "revoked") return "bad";
  if (status === "escalated" || status === "paused") return "warn";
  return "neutral";
}

export default async function MissionsPage() {
  const missions = await listMissions();
  const activeCount = missions.filter((mission) => mission.state.status === "running" || mission.state.status === "planned").length;
  const completedCount = missions.filter((mission) => mission.state.status === "completed").length;
  const boundaryCount = missions.reduce(
    (total, mission) =>
      total
      + mission.actions.filter((action) => action.route === "block" || action.route === "escalate").length
      + mission.escalations.filter((item) => !item.resolvedAt).length,
    0,
  );

  return (
    <div className="page">
      <section className="hero">
        <div className="hero-panel">
          <div className="eyebrow">Mission Control</div>
          <h1 className="page-title">Mission OS command surface</h1>
          <p className="page-copy">
            Sentinel now tracks mission authority, scope, action routing, artifacts, reviewer status, trace timeline, and stop/revoke controls as first-class product objects.
          </p>
          <div className="metric-grid">
            <Metric label="Missions" value={`${missions.length}`} sub="local mission state" />
            <Metric label="Active" value={`${activeCount}`} sub="planned or running" />
            <Metric label="Completed" value={`${completedCount}`} sub="success evaluated" />
            <Metric label="Boundaries" value={`${boundaryCount}`} sub="blocked or escalated" />
          </div>
        </div>

        <div className="panel">
          <SectionBand eyebrow="Doctrine" title="Mission authority">
            <div className="list">
              <div className="list-item">
                <strong>Permission once for the mission</strong>
                <p>The user delegates a bounded objective with explicit systems, actions, paths, duration, and budget.</p>
              </div>
              <div className="list-item">
                <strong>Autonomy inside the mission</strong>
                <p>Local reversible work executes without micro-approval when it stays inside the envelope.</p>
              </div>
              <div className="list-item">
                <strong>Escalation at the boundary</strong>
                <p>External, irreversible, sensitive, costly, ambiguous, or out-of-scope actions escalate or block.</p>
              </div>
            </div>
          </SectionBand>
        </div>
      </section>

      <section className="panel">
        <SectionBand eyebrow="Registry" title="Registered mission types">
          <div className="quality-grid">
            {Array.from(new Map(missions.map((mission) => [mission.missionType.id, mission.missionType])).values()).map((type) => (
              <div className="quality-card" data-pass={type.status === "enabled" ? "true" : "false"} key={type.id}>
                <div className="approval-row">
                  <strong>{type.label}</strong>
                  <Chip tone={type.status === "enabled" ? "good" : "warn"}>{type.status.replace("_", " ")}</Chip>
                </div>
                <p>{type.description}</p>
                <div className="watchlist-meta">
                  <span>{type.allowedActions.length} actions</span>
                  <span>{type.allowedTools.length} tools</span>
                  <span>{type.blackZoneActions.length} black-zone</span>
                </div>
              </div>
            ))}
          </div>
        </SectionBand>
      </section>

      <section className="panel">
        <SectionBand eyebrow="Missions" title="Mission board">
          <div className="board-grid">
            {missions.map((mission) => (
              <Link className="board-card" data-tone={statusTone(mission.state.status)} href={`/dashboard/missions/${mission.envelope.id}`} key={mission.envelope.id}>
                <div className="approval-row">
                  <h4>{mission.envelope.missionTitle}</h4>
                  <ArrowUpRight size={15} />
                </div>
                <p>{mission.envelope.missionObjective}</p>
                <div className="watchlist-meta">
                  <span>{mission.envelope.mode}</span>
                  <span>{mission.state.status}</span>
                  <span>{mission.actions.length} actions</span>
                  <span>{mission.artifacts.length} artifacts</span>
                </div>
              </Link>
            ))}
          </div>
        </SectionBand>
      </section>

      <section className="panel">
        <SectionBand
          eyebrow="Safety"
          title="Runtime powers remain disabled"
          action={<Chip tone="good"><ShieldCheck size={14} /> G13 UI only</Chip>}
        >
          <div className="watchlist-meta">
            <span>no shell</span>
            <span>no browser submit</span>
            <span>no real email send</span>
            <span>no desktop</span>
            <span>no payment</span>
            <span>no credential access</span>
          </div>
        </SectionBand>
      </section>
    </div>
  );
}
