# Mobile Command Relay Protocol

**Three-Platform Integration:** WhatsApp ↔ Clawdbot ↔ GitHub ↔ Cowork

## Task Routing Decision

**Default: Clawdbot handles tasks directly**

When Jeff sends a task via WhatsApp, Clawdbot evaluates:

### Execute Locally (Clawdbot):
- Quick queries and lookups
- Simple commands (echo, ls, grep, etc.)
- File operations (read, write, edit)
- Git operations (commit, push, pull)
- Data retrieval from existing files
- System status checks

### Ask Before Routing to Cowork:
- Heavy data analysis (aggregations, statistics, trends)
- Excel/CSV processing and visualization
- Complex multi-step workflows
- FL MMTC deep-dive analysis
- Tasks requiring multiple data sources

**Format when asking:**
```
🤔 This looks like [type] task. Route to Cowork for processing?

Reply:
• Y = Push to Cowork (heavier compute, ~5 min wait)
• N = I'll handle it now (faster, simpler approach)
```

**Cost Optimization Goal:**
- Minimize API calls by handling routine tasks locally
- Use Cowork only for tasks that benefit from its capabilities
- Jeff approves routing for cost control

## Workflow

### 1. Task Submission (WhatsApp → Clawdbot → GitHub)

**Jeff sends task via WhatsApp:**
```
"[task description]"
```

**Clawdbot evaluates and either:**

**A) Handles directly (default):**
1. Executes the task locally
2. Sends result to WhatsApp
3. Logs summary to GitHub (optional, for Cowork context)

**B) Asks to route to Cowork:**
1. Asks Jeff: "Route to Cowork? (Y/N)"
2. If Y: Creates `inbox/task.json` with:
   ```json
   {
     "id": "YYYYMMDD-HHMMSS",
     "timestamp": "ISO timestamp",
     "task": "exact task text",
     "requested_by": "jeff_mobile",
     "status": "pending"
   }
   ```
2. Commits and pushes to GitHub
3. Sends WhatsApp confirmation:
   ```
   ✅ Task sent to Cowork — it will run within 5 minutes. I will report back when done.
   📋 Task ID: [id]
   📍 Pushed to: [GitHub URL]
   ```

### 2. Task Execution (Cowork detects → processes → reports)

**Cowork (every 5 minutes):**
1. Pulls latest from GitHub
2. Checks for `inbox/task.json` with `status: "pending"`
3. **ON START:** Updates task.json status to "running" and sends to Clawdbot:
   ```
   [TASK START] ID: [id] | Started: [HH:MM UTC] | Task: [description]
   ```
4. Executes the task
5. **ON COMPLETION:** Sends result to Clawdbot:
   ```
   [COWORK RESULT] ID: [id] | Completed: [HH:MM UTC] | Duration: [time]
   
   [result summary or answer]
   ```
6. Updates task.json status to "completed" and commits

**Clawdbot (on receiving [TASK START]):**
- Forwards to Jeff's WhatsApp:
  ```
  🔄 **Task Started**
  📋 ID: [id]
  ⏱️ Start: [HH:MM UTC]
  📝 Task: [description]
  ```

**Clawdbot (on receiving [COWORK RESULT]):**
- Forwards to Jeff's WhatsApp:
  ```
  ✅ **Task Completed**
  📋 ID: [id]
  ⏱️ End: [HH:MM UTC]
  ⏱️ Duration: [time]
  
  📊 **Result:**
  [result text]
  ```

## Task JSON Schema

```json
{
  "id": "string (YYYYMMDD-HHMMSS)",
  "timestamp": "ISO 8601 timestamp",
  "task": "string (exact task description)",
  "requested_by": "jeff_mobile | clawdbot_test",
  "status": "pending | running | completed | failed",
  "started_at": "ISO timestamp (optional)",
  "completed_at": "ISO timestamp (optional)",
  "duration_seconds": "number (optional)",
  "result": "string (optional)"
}
```

## Communication Paths

1. ✅ **WhatsApp → Clawdbot → GitHub** (task submission)
2. ✅ **Cowork → Clawdbot → WhatsApp** (results)
3. ✅ **Clawdbot → Cowork + WhatsApp** (direct commands)
4. ✅ **Cowork → GitHub → Clawdbot → WhatsApp** (task status updates)

## Message Format Requirements

### From Cowork to Clawdbot

**Task Start:**
```
[TASK START] ID: 20260323-031820 | Started: 03:30 UTC | Task: Query top 3 operators
```

**Task Result:**
```
[COWORK RESULT] ID: 20260323-031820 | Completed: 03:32 UTC | Duration: 2m 15s

Top 3 FL MMTC operators by avg weekly THC (Q1 2026):
1. Trulieve: 117.2M mg avg/week
2. MÜV: 61.5M mg avg/week  
3. Curaleaf: 48.1M mg avg/week
```

### Clawdbot Detection Rules

- Message starting with `[TASK START]` → Parse and relay start notification to WhatsApp
- Message starting with `[COWORK RESULT]` → Parse and relay completion + result to WhatsApp
- All other messages from Cowork → Log but don't auto-relay

## Task Execution Log

When Clawdbot handles tasks directly, it can optionally log to GitHub:

**File:** `logs/clawdbot-tasks.jsonl`

**Format:**
```jsonl
{"id":"20260323-034500","timestamp":"2026-03-23T03:45:00Z","task":"ls -la","executed_by":"clawdbot","result":"[output]","duration_ms":120}
```

This keeps Cowork informed of what's been done without requiring full routing.

---

**Last Updated:** 2026-03-23 03:41 UTC
**Version:** 1.2 (added smart routing: Clawdbot-first with optional Cowork escalation)
