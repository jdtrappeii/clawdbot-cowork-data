# Mobile Command Relay Protocol

**Three-Platform Integration:** WhatsApp ↔ Clawdbot ↔ GitHub ↔ Cowork

## Workflow

### 1. Task Submission (WhatsApp → Clawdbot → GitHub)

**Jeff sends task via WhatsApp:**
```
"[task description]"
```

**Clawdbot immediately:**
1. Creates `inbox/task.json` with:
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

---

**Last Updated:** 2026-03-23 03:31 UTC
**Version:** 1.1 (added task start/end timestamps)
