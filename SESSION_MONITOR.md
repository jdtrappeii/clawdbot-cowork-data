# Session Activity Monitor

**Auto-sleep protocol to optimize resource usage and API costs**

## State Machine

### States:
- **ACTIVE** - Session is being used, Cowork relay running
- **IDLE** - 15 min of inactivity, warning sent
- **DORMANT** - No response to warning, Cowork relay paused

## Activity Detection

**Session is considered ACTIVE when ANY message received from:**
1. Jeff via WhatsApp
2. Clawdbot (this bot)
3. Cowork (via [TASK START] or [COWORK RESULT])

**Activity resets the 15-minute timer.**

## Workflow

### 1. Active → Idle (15 min no activity)

**Clawdbot sends to WhatsApp:**
```
🔔 Session inactive for 15 min. Still working on this project?

Reply anything to keep active, or session will go dormant in 5 min.
```

**If ANY response within 5 min:**
- State → ACTIVE
- Timer resets
- Cowork relay continues

### 2. Idle → Dormant (no response for 5 min)

**Clawdbot:**
1. Marks session DORMANT
2. Creates flag file: `.session_dormant`
3. Sends to WhatsApp:
   ```
   💤 Session dormant - Cowork relay paused to save resources.
   
   Send any message to reactivate automatically.
   ```

**Cowork:**
- Detects `.session_dormant` flag
- Stops checking `inbox/task.json` every 5 min
- Saves API calls

### 3. Dormant → Active (any message)

**On ANY message from Jeff/Clawdbot/Cowork:**

**Clawdbot:**
1. Removes `.session_dormant` flag
2. Commits to GitHub
3. Sends to WhatsApp:
   ```
   🔄 Session reactivated - Cowork relay resumed.
   
   Cowork is now checking for tasks every 5 min again.
   ```

**Cowork:**
- Detects flag removal
- Resumes task checking every 5 min

## State Persistence

**File:** `.session_state.json`

```json
{
  "state": "ACTIVE | IDLE | DORMANT",
  "last_activity": "ISO timestamp",
  "idle_warning_sent_at": "ISO timestamp or null",
  "dormant_since": "ISO timestamp or null"
}
```

## Cowork Integration

**Cowork checks on every 5-min cycle:**

```python
# Pseudo-code for Cowork
if os.path.exists('.session_dormant'):
    # Session is dormant, skip task checking
    log("Session dormant - skipping task check")
    return
    
# Session active, check for tasks
check_inbox_for_tasks()
```

## Benefits

**Cost Savings:**
- ✅ No API calls during dormant periods
- ✅ Cowork doesn't poll every 5 min when idle
- ✅ Resources freed for other work

**Auto-Resume:**
- ✅ Any activity instantly reactivates
- ✅ No manual intervention needed
- ✅ Seamless user experience

**Activity Types That Reset Timer:**
- WhatsApp message from Jeff
- Clawdbot executing a task
- Cowork sending [TASK START] or [COWORK RESULT]
- Any interaction in the three-platform system

## Implementation Notes

**Clawdbot responsibilities:**
- Track last activity timestamp
- Send 15-min inactivity warning
- Create/remove `.session_dormant` flag
- Update `.session_state.json`
- Notify WhatsApp of state changes

**Cowork responsibilities:**
- Check for `.session_dormant` before polling
- Skip task checking if dormant
- Resume when flag removed

---

**Last Updated:** 2026-03-23 03:51 UTC
**Version:** 1.0 (initial session activity monitor)