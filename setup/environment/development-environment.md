# Setup Development Environment for Valuestrea OS


## Required tools and applications
You need to install these tools
```
winget install Microsoft.PowerShell
winget install Anaconda.Miniconda3
winget install Microsoft.VisualStudioCode
```


## Bootstrap
We have a basic setup script:
```powershell
pwsh ./scripts/bootstrap.ps1
```
This will
* Create envio


## Work
To start orking in the project we have this script:
```powershell
pwsh ./scripts/dev.ps1
```

This will 
* activate correct conda environment (valuestream-os)
* Open VS Code
