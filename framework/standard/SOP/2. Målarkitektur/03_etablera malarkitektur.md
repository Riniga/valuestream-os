# SOP 3: Etablera målarkitektur

## 1. Syfte

Etablera en sammanhängande målarkitektur genom att definiera integrationer, principer och kvalitetskrav samt sammanställa dessa till en tydlig och kommunicerbar helhet.

---

## 2. Kontext

- Processteg: Målarkitektur
- Delprocess: Etablera målarkitektur

---

## 3. Input

- Systemlandskap
- Domänmodell
- Omfattning och Strukturerad Backlog


---

## 4. Output

- Integrationsarkitektur
- Arkitekturprinciper
- Icke-funktionella krav
- Målarkitektur

---

## 5. RACI

- R: Lösningsarkitekt
- A: Enterprise Arkitekt
- C: Teknisk Lead, DevOps, Business Analyst
- I: Beställare

---

## 6. Arbetssteg

### Steg 1: Definiera integrationsarkitektur
1. Identifiera integrationer mellan system baserat på systemlandskap.
2. Definiera integrationsmönster (t.ex. API, event, batch).
3. Kartlägg dataflöden och ansvarsfördelning.
4. Säkerställ koppling till domänmodell och arkitekturmål.

---

### Steg 2: Fastställ arkitekturprinciper
5. Identifiera behov av principer baserat på mål och lösningens komplexitet.
6. Formulera principer (t.ex. API-first, löst kopplade system, säkerhet som standard).
7. Säkerställ att principer stödjer integrationer och behov.
8. Strukturera och konsolidera principerna.

---

### Steg 3: Definiera NFR (kvalitetskrav)
9. Identifiera relevanta kvalitetsområden (prestanda, tillgänglighet, säkerhet, drift).
10. Definiera mätbara krav per område.
11. Definiera krav på observability (loggning, monitorering).
12. Säkerställ att NFR stödjer arkitekturprinciper och behov.

---

### Steg 4: Sammanställ målarkitektur
13. Sammanställ alla artefakter i en helhetsbild.
14. Säkerställ spårbarhet mellan krav, domän och arkitektur.
15. Strukturera målarkitekturen i ett tydligt format.
16. Säkerställ att principer och NFR efterlevs.

---

### Steg 5: Validera och fastställ
17. Kvalitetssäkra med teknisk lead, DevOps och relevanta roller.
18. Säkerställ att arkitekturen är tillräcklig för roadmap.
19. Kommunicera målarkitekturen.
20. Fastställ målarkitektur (beslut av A).
