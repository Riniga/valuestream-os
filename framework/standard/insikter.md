# Mina tankar

insikter kring ramverket och hur det hänger samman. Det är ganska komplext och jag behöver nog göra det enklare....

## Artifakter:

filnamn är encoding från namn (exempelvis: Mål & Vision blir mal_vision)
filnamn i input/output blir samma som mallens filnamn (finns logik i kod som avgör, jag vill inte ha denna logik)

Mall i Beskrivning används inte??

## RACI

RACI katalogen används bara för att synliggöra för användarna. inte agenter

## SOP

RACI i en SOP bestämmer vilka agenter som skall agera...

## Agenter

varje agent beskrivs i sin fil
manifest.json konfigurerar agenter och hänvisar till fil samt
actor_kind = automated eller human byt denna för att låta människor interagera

Beställare
Business Analyst
Verksamhetsexperter
Användarrepresentanter

Projektledare

Enterprise Arkitekt
Lösningsarkitekt
Teknisk Lead

DevOps
Utvecklare

## kommandon

python -m src.cli.run --run-id pernilla --process "1. Kravställning.md" flow

## TODO

- saknas en fil även bestallning.md p.g.a. får man inte fel att filen saknas utan att filen avslagits.

- output run ska gå till separat repp
- Itterate: Om vi kör om ett processsteg. Tillse att vi uppdaterar utifrån tidigare insikter och inte bygger om från början....

Uppdatera artifacts_sop_mapping.yml
