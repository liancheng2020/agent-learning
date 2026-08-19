import { createHash, randomUUID } from "node:crypto";

export class ApprovalStore {
  constructor() { this.items = new Map(); }
  request({ runId, patch, risk }) {
    if (risk !== "requires-review") return null;
    const actionId = randomUUID();
    const patchHash = digest(patch);
    const approval = { actionId, runId, patchHash, status: "needs_approval", createdAt: new Date().toISOString() };
    this.items.set(actionId, approval);
    return approval;
  }
  approve(actionId, { reviewer = "local-reviewer", patch } = {}) {
    const approval = this.items.get(actionId);
    if (!approval) throw new Error("unknown approval action");
    if (approval.status !== "needs_approval") throw new Error(`approval is already ${approval.status}`);
    if (patch && digest(patch) !== approval.patchHash) throw new Error("patch changed after approval was requested");
    const approved = { ...approval, status: "approved", reviewer, approvedAt: new Date().toISOString() };
    this.items.set(actionId, approved);
    return approved;
  }
}

function digest(value) { return createHash("sha256").update(value).digest("hex"); }
