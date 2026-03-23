# New Simplified Architecture (2026-03-23)

**Decision:** Direct WhatsApp ↔ Clawdbot with GitHub as audit log only

---

## Communication Flow

### **Primary Path (Real-Time):**
```
WhatsApp (Jeff)
    ↓
Clawdbot (handles all tasks)
    ↓
WhatsApp (results)
```

### **GitHub Role (Async Audit):**
```
Clawdbot → GitHub (push updates/results)
    ↓
Cowork (pulls when Jeff opens desktop session)
```

---

## What Changed

### **REMOVED:**
- ❌ `inbox/task.json` command queue
- ❌ Cowork auto-polling every 5 min
- ❌ `SESSION_MONITOR.md` complexity
- ❌ `.session_state.json` tracking
- ❌ Automatic command relay

### **KEPT:**
- ✅ GitHub repo for data storage
- ✅ Clawdbot as primary execution engine
- ✅ WhatsApp as command interface
- ✅ Cowork for heavy analysis (manual)

---

## New Workflow

### **For Simple Tasks:**
1. Jeff sends task via WhatsApp
2. Clawdbot executes immediately
3. Results sent to WhatsApp
4. Summary logged to GitHub

### **For Complex Analysis:**
1. Jeff sends request via WhatsApp
2. Clawdbot: "This needs Cowork - opening desktop session?"
3. If Yes: Jeff opens Cowork desktop
4. Cowork pulls latest from GitHub
5. Cowork performs analysis
6. Results pushed to GitHub
7. Clawdbot notifies Jeff via WhatsApp

---

## Benefits

✅ **Faster** - No 5-min polling delay
✅ **Simpler** - No session state complexity
✅ **Cheaper** - No constant API calls from Cowork
✅ **Clearer** - Jeff controls when Cowork runs
✅ **More reliable** - No polling bugs

---

## Cowork's New Role

**FROM:** Auto-polling agent checking inbox every 5 min
**TO:** On-demand analyst opened when Jeff needs it

**When to use Cowork:**
- Heavy data analysis (FL MMTC queries)
- Excel/visualization work
- Complex multi-step workflows
- When Jeff explicitly opens desktop session

**Cowork does NOT:**
- Poll for tasks automatically
- Run background scheduled tasks
- Monitor WhatsApp conversations

---

## GitHub Structure (Audit Log)

```
clawdbot-cowork-data/
├── logs/
│   ├── 2026-03-23-tasks.jsonl  # Daily task log
│   └── ...
├── projects/
│   └── ommu-2026-q1/  # Data projects
└── ARCHITECTURE.md  # This file
```

**No more:**
- `inbox/task.json` (removed)
- `.session_state.json` (removed)  
- `SESSION_MONITOR.md` (archived)

---

**Effective:** 2026-03-23 04:08 UTC
**Status:** Active
**Confirmed by:** Jeff via WhatsApp
