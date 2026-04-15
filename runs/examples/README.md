# Example Run Navigation

Det här är en referensyta som visar hur en publicerad run bör presenteras, utan att checka in verkliga runtime-filer.

## Tänkta delar i en publicerad run

En run som delas med stakeholders bör normalt innehålla:

- `README.md` – sammanfattning, mål, status och nyckelresultat
- `artifacts/` – levererade artefakter eller länkar till dem
- `approval_decisions.json` – beslut och godkännanden
- `consultation_responses.json` – expert- eller stakeholderinput
- `artifact_state.json` – status för producerade artefakter
- `run_log.json` – exekveringshändelser och tidslinje

## Rekommenderad läsordning

1. Läs runnens `README.md`
2. Titta på viktigaste artefakterna
3. Läs beslut och konsultationer
4. Bekräfta status i state-filerna

## Koppling till framework

En run ska alltid gå att förstå tillsammans med frameworket:

- [Framework index](../../framework/standard/INDEX.md)
- [Process overview](../../framework/standard/processes/Process.md)
- [Artifacts overview](../../framework/standard/artifacts/Artifacts.md)

## Kommentar

När `valuestream-os-data` finns kan detta exempel ersättas eller kompletteras med verkliga, publicerade runs.
