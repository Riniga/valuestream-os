# Plan: Agent Orchestration Framework MVP — Flödesdefinition

## Syfte

Definiera exakt vilket flöde, vilka agentroller och vilka artifakter som ingår i den första körningsbara multi-agent-kedjan.

---

## Valt flöde: Business Analyst → UX → Business Analyst

Flödet spänner över tre processsteg i Kravställning och bevisar att:
- En agent (BA) producerar en artefakt som nästa agent (UX) konsumerar.
- En agent (UX) producerar en artefakt som konsumeras av en tredje körning (BA igen).
- Output från ett steg registreras explicit och görs tillgänglig som input i nästa steg.

```
[overgripande_behov.md]
         │
    ┌────▼──────────────────────┐
    │ Step 1: Business Analyst  │  SOP 1 – Vision & målbild
    │ Producerar: vision_och_   │
    │            malbild.md     │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Step 2: UX                │  SOP 6 – User Journeys
    │ Input:   vision_och_      │
    │          malbild.md +     │
    │          overgripande_    │
    │          behov.md         │
    │ Producerar: user_         │
    │             journeys.md   │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Step 3: Business Analyst  │  SOP 7 – Skapa Story Map
    │ Input:   user_journeys.md │
    │          vision_och_      │
    │          malbild.md       │
    │ Producerar: story_map.md  │
    └───────────────────────────┘
```

---

## Steg 1 — Business Analyst: Vision & målbild

| Fält              | Värde                                     |
| ----------------- | ----------------------------------------- |
| step_id           | ba-vision                                 |
| agent_id          | business-analyst                          |
| SOP               | docs/SOP/1.Kravställning/01_vision_och_malbild.md |
| Artefaktnamn      | Vision & målbild                          |
| Output-fil        | vision_och_malbild.md                     |
| Input-filer       | overgripande_behov.md                     |

---

## Steg 2 — UX: User Journeys

| Fält              | Värde                                     |
| ----------------- | ----------------------------------------- |
| step_id           | ux-journeys                               |
| agent_id          | ux                                        |
| SOP               | docs/SOP/1.Kravställning/06_user_journeys.md |
| Artefaktnamn      | User journeys                             |
| Output-fil        | user_journeys.md                          |
| Input-filer       | vision_och_malbild.md, overgripande_behov.md |

**Not:** SOP 6 specificerar Domänmodell, User Stories och Stakeholderkarta som ideala input. I MVP:n används vision_och_malbild.md + overgripande_behov.md som pragmatiskt substitut för att säkerställa ett fungerande artefaktflöde utan manuell mellandata.

---

## Steg 3 — Business Analyst: Story Map

| Fält              | Värde                                     |
| ----------------- | ----------------------------------------- |
| step_id           | ba-storymap                               |
| agent_id          | business-analyst                          |
| SOP               | docs/SOP/1.Kravställning/07_skapa_story_map.md |
| Artefaktnamn      | Story map                                 |
| Output-fil        | story_map.md                              |
| Input-filer       | user_journeys.md, vision_och_malbild.md   |

---

## Agentregister

| agent_id           | Agent-fil                   | RACI-roll         |
| ------------------ | --------------------------- | ----------------- |
| business-analyst   | docs/agents/business-analyst.md | Business Analyst |
| ux                 | docs/agents/ux.md           | UX                |

---

## Verifieringspunkter

- [ ] Körning startar från `runs/<run-id>/input/overgripande_behov.md`
- [ ] Steg 1 producerar `runs/<run-id>/output/vision_och_malbild.md`
- [ ] Output från Steg 1 kopieras automatiskt till input-dir för Steg 2
- [ ] Steg 2 producerar `runs/<run-id>/output/user_journeys.md`
- [ ] Output från Steg 2 kopieras automatiskt till input-dir för Steg 3
- [ ] Steg 3 producerar `runs/<run-id>/output/story_map.md`
- [ ] Körningsstate och artefaktstatus är spårbara i `runs/<run-id>/`
- [ ] Steg med saknad input hoppas över och rapporteras tydligt
