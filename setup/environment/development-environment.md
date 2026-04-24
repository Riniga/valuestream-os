# Setup Development Environment for ValueStream OS

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

This may be executed within VS Code by running Task: Bootstrap

## Manuellt

1. conda create -n
2. conda env create -n valuesstream-os -f environment.yml
3. conda activate valuesstream-os
4. cursor/code .

## Work

To start working in the project we have this script:

```powershell
pwsh ./scripts/dev.ps1
```

This will

- activate correct conda environment (valuestream-os)
- Open VS Code
