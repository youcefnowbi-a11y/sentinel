import { notFound } from "next/navigation";
import { MissionControls } from "@/components/mission-controls";
import { Chip, Metric, SectionBand } from "@/components/ui";
import { getMission } from "@/lib/mission-store";
import type { MissionActionRoute, MissionStatus } from "@/lib/types";

export const dynamic = "force-dynamic";

function statusTone(status: MissionStatus): "neutral" | "good" | "warn" | "bad" {
  if (status === "completed") return "good";
  if (status === "failed" || status === "stopped" || status === "revoked") return "bad";
  if (status === "escalated" || status === "paused") return "warn";
  return "neutral";
}

function routeTone(route: MissionActionRoute): "neutral" | "good" | "warn" | "bad" {
  if (route === "auto_execute") return "good";
  if (route === "log_and_continue") return "neutral";
  if (route === "escalate") return "warn";
  return "bad";
}

function traceTone(eventType: string): "neutral" | "good" | "warn" | "bad" {
  if (eventType.includes("completed") || eventType.includes("executed")) return "good";
  if (eventType.includes("blocked") || eventType.includes("revoked") || eventType.includes("failed")) return "bad";
  if (eventType.includes("escalated") || eventType.includes("paused")) return "warn";
  return "neutral";
}

export default async function MissionDetailPage({ params }: { params: Promise<{ missionId: string }> }) {
  const { missionId } = await params;
  const mission = await getMission(missionId);

  if (!mission) {
    notFound();
  }

  const autoCount = mission.actions.filter((action) => action.route === "auto_execute" || action.route === "log_and_continue").length;
  const blockedCount = mission.actions.filter((action) => action.route === "block").length;
  const escalationCount = mission.actions.filter((action) => action.route === "escalate").length + mission.escalations.filter((item) => !item.resolvedAt).length;

  return (
    <div className="page">
      <section className="hero">
        <div className="hero-panel">
          <div className="eyebrow">Mission Detail</div>
          <h1 className="page-title">{mission.envelope.missionTitle}</h1>
          <p className="page-copy">{mission.envelope.missionObjective}</p>
          <div className="metric-grid">
            <Metric label="Status" value={mission.state.status} sub={mission.envelope.mode} />
            <Metric label="Auto work" value={`${autoCount}`} sub="inside mission" />
            <Metric label="Boundaries" value={`${blockedCount + escalationCount}`} sub="blocked or escalated" />
            <Metric label="Artifacts" value={`${mission.artifacts.length}`} sub="indexed local outputs" />
          </div>
          <div className="section-actions" style={{ marginTop: 16 }}>
            <Chip tone={statusTone(mission.state.status)}>{mission.state.status}</Chip>
            <Chip tone={mission.reviewer.ready ? "good" : "warn"}>{mission.reviewer.ready ? "review passed" : "review issues"}</Chip>
            <Chip tone="neutral">{mission.missionType.label}</Chip>
          </div>
        </div>

        <div className="panel">
          <SectionBand eyebrow="Kill switch" title="Mission control">
            <MissionControls missionId={mission.envelope.id} initialStatus={mission.state.status} />
          </SectionBand>
        </div>
      </section>

      <section className="panel">
        <SectionBand eyebrow="Authority Preview" title="Mission Authority Envelope">
          <div className="detail-grid">
            <div className="detail-box">
              <div className="detail-label">Will act without asking</div>
              <div className="detail-body">
                <div className="watchlist-meta">
                  {mission.envelope.allowedActions.slice(0, 8).map((item) => <span key={item}>{item}</span>)}
                </div>
              </div>
            </div>
            <div className="detail-box">
              <div className="detail-label">Will still ask or block</div>
              <div className="detail-body">
                <div className="watchlist-meta">
                  {mission.envelope.escalationTriggers.map((item) => <span key={item}>{item}</span>)}
                </div>
              </div>
            </div>
            <div className="detail-box">
              <div className="detail-label">Cannot do in G13</div>
              <div className="detail-body">
                <div className="watchlist-meta">
                  {mission.envelope.forbiddenActions.slice(0, 8).map((item) => <span key={item}>{item}</span>)}
                </div>
              </div>
            </div>
          </div>
          <div className="footer-strip">
            <span>Allowed paths: {mission.envelope.allowedPaths.join(", ")}</span>
            <span>Budget: ${mission.state.costUsed.toFixed(2)} / ${mission.envelope.maxCostUsd.toFixed(2)}</span>
            <span>Actions: {mission.state.actionCount} / {mission.envelope.maxActions}</span>
          </div>
        </SectionBand>
      </section>

      <section className="columns-2">
        <div className="panel">
          <SectionBand eyebrow="Actions" title="Autonomy routing">
            <div className="list">
              {mission.actions.map((action) => (
                <div className="list-item" key={action.id}>
                  <div className="approval-row">
                    <strong>{action.actionType}</strong>
                    <Chip tone={routeTone(action.route)}>{action.route}</Chip>
                  </div>
                  <p>{action.intent}</p>
                  <div className="watchlist-meta">
                    <span>{action.tool}</span>
                    <span>{action.reversibility}</span>
                    <span>{action.externality}</span>
                    <span>{action.sensitivity}</span>
                    <span>risk {action.riskScore}</span>
                  </div>
                </div>
              ))}
            </div>
          </SectionBand>
        </div>

        <div className="panel">
          <SectionBand eyebrow="Artifacts" title="Mission Artifact Index">
            <div className="list">
              {mission.artifacts.map((artifact) => (
                <div className="list-item" key={artifact.id}>
                  <div className="approval-row">
                    <strong>{artifact.path}</strong>
                    <Chip tone={artifact.canRollback ? "good" : "warn"}>{artifact.canRollback ? "rollback metadata" : "fixed"}</Chip>
                  </div>
                  <p>{artifact.artifactType} / refs {artifact.evidenceRefs.length}</p>
                  <span className="page-note">Created by {artifact.createdByActionId || "mission"}</span>
                </div>
              ))}
            </div>
          </SectionBand>
        </div>
      </section>

      <section className="columns-2">
        <div className="panel">
          <SectionBand eyebrow="Reviewer" title="Mission success gate">
            {mission.reviewer.issues.length > 0 ? (
              <div className="list">
                {mission.reviewer.issues.map((issue) => (
                  <div className="list-item" key={`${issue.code}-${issue.message}`}>
                    <div className="approval-row">
                      <strong>{issue.code}</strong>
                      <Chip tone={issue.severity === "critical" || issue.severity === "high" ? "bad" : "warn"}>{issue.severity}</Chip>
                    </div>
                    <p>{issue.message}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">ReviewerLite found no blocking issues for this mission.</div>
            )}
          </SectionBand>
        </div>

        <div className="panel">
          <SectionBand eyebrow="Escalation" title="Boundary requests">
            {mission.escalations.length > 0 ? (
              <div className="list">
                {mission.escalations.map((request) => (
                  <div className="list-item" key={request.id}>
                    <div className="approval-row">
                      <strong>{request.reason}</strong>
                      <Chip tone={request.resolvedAt ? "good" : "warn"}>{request.resolvedAt ? "resolved" : "open"}</Chip>
                    </div>
                    <p>{request.impactSummary}</p>
                    <div className="watchlist-meta">
                      {request.options.map((option) => <span key={option}>{option}</span>)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">No unresolved escalation requests.</div>
            )}
          </SectionBand>
        </div>
      </section>

      <section className="panel">
        <SectionBand eyebrow="Trace" title="Mission timeline">
          <div className="trace-list">
            {mission.traceEvents.map((event) => (
              <div className="trace-row" key={event.id}>
                <span className="trace-dot" data-tone={traceTone(event.eventType)} />
                <div>
                  <div className="approval-row">
                    <strong>{event.eventType}</strong>
                    <Chip tone={event.actor === "user" ? "warn" : "neutral"}>{event.actor}</Chip>
                  </div>
                  <p>{event.summary}</p>
                  <div className="trace-meta">
                    <span>{new Date(event.timestamp).toLocaleString()}</span>
                    {event.actionId ? <span>{event.actionId}</span> : null}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SectionBand>
      </section>
    </div>
  );
}
