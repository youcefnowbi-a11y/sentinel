import { NextRequest, NextResponse } from "next/server";
import { updateMissionStatus } from "@/lib/mission-store";
import type { MissionStatus } from "@/lib/types";

const allowed = new Set<MissionStatus>(["paused", "stopped", "revoked"]);

export async function POST(request: NextRequest, { params }: { params: Promise<{ missionId: string }> }) {
  const { missionId } = await params;
  const body = (await request.json().catch(() => ({}))) as { status?: MissionStatus };
  const status = body.status;

  if (!status || !allowed.has(status)) {
    return NextResponse.json({ error: "Unsupported mission status transition." }, { status: 400 });
  }

  const mission = await updateMissionStatus(missionId, status as Extract<MissionStatus, "paused" | "stopped" | "revoked">);
  if (!mission) {
    return NextResponse.json({ error: "Mission not found." }, { status: 404 });
  }

  return NextResponse.json({ mission });
}
