"use client";

import { Pause, OctagonX, ShieldX } from "lucide-react";
import { useState } from "react";
import type { MissionRecord, MissionStatus } from "@/lib/types";

export function MissionControls({
  missionId,
  initialStatus,
}: {
  missionId: string;
  initialStatus: MissionStatus;
}) {
  const [status, setStatus] = useState(initialStatus);
  const [busy, setBusy] = useState<MissionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function update(nextStatus: Extract<MissionStatus, "paused" | "stopped" | "revoked">) {
    setBusy(nextStatus);
    setError(null);
    try {
      const response = await fetch(`/api/missions/${encodeURIComponent(missionId)}/status`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      });
      const payload = (await response.json()) as { mission?: MissionRecord; error?: string };
      if (!response.ok || !payload.mission) {
        throw new Error(payload.error || "Mission status update failed.");
      }
      setStatus(payload.mission.state.status);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Mission status update failed.");
    } finally {
      setBusy(null);
    }
  }

  const closed = status === "completed" || status === "failed" || status === "stopped" || status === "revoked";

  return (
    <div className="inline-action-stack">
      <div className="section-actions">
        <button className="secondary-btn" disabled={closed || busy !== null} onClick={() => void update("paused")} type="button">
          <Pause size={16} />
          <span>{busy === "paused" ? "Pausing" : "Pause"}</span>
        </button>
        <button className="ghost-btn" disabled={closed || busy !== null} onClick={() => void update("stopped")} type="button">
          <OctagonX size={16} />
          <span>{busy === "stopped" ? "Stopping" : "Stop"}</span>
        </button>
        <button className="ghost-btn" disabled={status === "revoked" || busy !== null} onClick={() => void update("revoked")} type="button">
          <ShieldX size={16} />
          <span>{busy === "revoked" ? "Revoking" : "Revoke"}</span>
        </button>
      </div>
      {error ? <div className="inline-alert">{error}</div> : null}
      <span className="page-note">Current local status: {status.replace("_", " ")}</span>
    </div>
  );
}
