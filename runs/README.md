# Runs Directory

`runs/` är den lokala katalog där runtime lägger körningsspecifik state, loggar, input och output.

Katalogen har två roller just nu:

1. lokal arbetsyta för orchestratorn
2. dokumenterad interim-ingång till resultatdelen i MVP 05

Det betyder att:

- verkliga run-mappar som skapas av körningar normalt inte versionshanteras
- de mänskligt läsbara entry-filerna i denna katalog däremot committas
- framtida publicerade runs förväntas flyttas eller speglas till `valuestream-os-data`

Se [INDEX.md](./INDEX.md) för stakeholder-orienterad navigation.
