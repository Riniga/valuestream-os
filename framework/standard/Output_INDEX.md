# ValueStream OS Runs – Index

Central index of execution runs and their results.

> **Note:** This is the primary runs index. As we grow, runs will migrate to a dedicated data repository (`valuestream-os-data`) to separate code from execution results. For now, both index and results are stored here.

---

## 📊 Completed Runs

| Run ID | Process Steps | Status | Start Date | Team | Key Artifacts |
|--------|---------------|--------|-----------|------|--------------|
| [middag-tillsammans](./middag-tillsammans/) | Kravställning, Målarkitektur | ✅ Completed | 2026-03-15 | Framework team | Vision, User Stories, Architecture |

---

## 🔍 How to Read Run Results

Each run folder contains:

```
runs/[RUN-ID]/
├─ README.md (or similar)           ← Start here for run summary [planned]
├─ run_log.json                     ← Timestamped execution log
├─ run_state.json                   ← Current run state
├─ approval_decisions.json          ← What was approved and by whom
├─ consultation_requests.json       ← Stakeholder questions
├─ consultation_responses.json      ← Responses from experts
├─ artifact_state.json              ← Status of each artifact
├─ expert_context.json              ← Expert inputs used
├─ informed_role_briefs.json        ← Who was informed
├─ input/                           ← Input artifacts
└─ output/                          ← Final artifacts & results
```

---

## 📁 Available Runs

### Run: middag-tillsammans

**Process Steps:** Kravställning (Requirements) → Målarkitektur (Architecture Design)  
**Status:** ✅ Completed  
**Duration:** 2-week exploration  
**Key Files:**

- `run_log.json` – Execution timeline
- `run_state.json` – Final state snapshot
- `approval_decisions.json` – Approval records
- `artifact_state.json` – What was completed
- `expert_context.json` – Expert input & stakeholder involvement

**What to look for:**
- See `approval_decisions.json` for what was approved
- Check `artifact_state.json` to see completion status
- Review `run_log.json` for timeline and milestones
- Look at `informed_role_briefs.json` for stakeholder communication

---

## 🚀 Next Steps

### In Progress
- [ ] Create run-specific README files ([template available](../framework/standard/artifacts/templates/run-README.md.template))
- [ ] Populate runs/INDEX.md with quick summary tables
- [ ] Add run timelines and phase completion status

### Planned (Separate PR)
- [ ] Move `runs/` to dedicated `valuestream-os-data` repository
- [ ] Set up cross-repository navigation links
- [ ] Implement full run management and archive structure

---

## 📖 Understanding the Metadata Files

Each run stores JSON files capturing framework execution data:

| File | Purpose | Use Case |
|------|---------|----------|
| `run_log.json` | Timestamped log of all activities | Track timeline, see when each step happened |
| `run_state.json` | Current state of the run | Snapshot of what was accomplished |
| `approval_decisions.json` | Record of all approvals | Who approved what artifacts and decisions |
| `consultation_requests.json` | Questions asked to experts | See what was discussed and clarified |
| `consultation_responses.json` | Responses from experts | Understand expert input and guidance |
| `artifact_state.json` | Completion status of each artifact | Track which outputs are draft/final/approved |
| `expert_context.json` | Background on experts involved | See expertise and input sources |
| `informed_role_briefs.json` | Communication log | Understand how stakeholders were kept informed |

---

## 🔗 Links

- **← Back to [Home](/)** or **Framework Overview:** [ValueStream OS Framework](../framework/standard/INDEX.md)
- **Using our framework?** See [Process Overview](../framework/standard/processes/Process.md)

---

**Last Updated:** 2026-04-01  
**Repository:** valuestream-os (primary) + valuestream-os-data (planned)  
**Version:** 1.0

---

*This is the beginning of run tracking. As we execute more initiatives through the framework, this index will grow.*
