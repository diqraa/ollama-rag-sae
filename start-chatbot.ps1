param(
    [switch]$InstallOnly
)

$ErrorActionPreference = "Stop"
$repositoryRoot = $PSScriptRoot
Set-Location $repositoryRoot

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{
            Executable = $python.Source
            Arguments = @()
        }
    }

    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        return @{
            Executable = $launcher.Source
            Arguments = @("-3")
        }
    }

    throw "Python 3.10+ est requis. Installe Python depuis https://www.python.org/downloads/ puis relance ce script."
}

function Get-OllamaModels {
    try {
        $response = Invoke-RestMethod `
            -Uri "http://127.0.0.1:11434/api/tags" `
            -TimeoutSec 2
        return $response.models
    }
    catch [System.Net.WebException] {
        return $null
    }
}

try {
    Write-Host "=== Assistant SAE - preparation du lancement ===" -ForegroundColor Cyan

    $pythonCommand = Get-PythonCommand
    $pythonVersion = (
        & $pythonCommand.Executable @($pythonCommand.Arguments) --version 2>&1 |
            Out-String
    ).Trim()
    if ($LASTEXITCODE -ne 0 -or $pythonVersion -notmatch "Python (\d+)\.(\d+)") {
        throw "Impossible de verifier la version de Python."
    }
    if ([int]$Matches[1] -lt 3 -or ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -lt 10)) {
        throw "Python 3.10 ou une version plus recente est requis. Version trouvee : $pythonVersion"
    }

    $venvPython = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "Creation de l'environnement Python..."
        & $pythonCommand.Executable @($pythonCommand.Arguments) -m venv (Join-Path $repositoryRoot ".venv")
        if ($LASTEXITCODE -ne 0) {
            throw "La creation de l'environnement Python a echoue."
        }
    }

    Write-Host "Verification et installation des dependances..."
    & $venvPython -m pip install --quiet --disable-pip-version-check -r (Join-Path $repositoryRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "L'installation des dependances a echoue. Verifie ta connexion puis relance le script."
    }

    $ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollamaCommand) {
        throw "Ollama est requis. Installe-le depuis https://ollama.com/download/windows puis relance ce script."
    }

    $models = Get-OllamaModels
    if ($null -eq $models) {
        Write-Host "Demarrage du service Ollama..."
        Start-Process -FilePath $ollamaCommand.Source -ArgumentList "serve" -WindowStyle Hidden

        for ($attempt = 0; $attempt -lt 30 -and $null -eq $models; $attempt++) {
            Start-Sleep -Seconds 2
            $models = Get-OllamaModels
        }
    }
    if ($null -eq $models) {
        throw "Ollama ne repond pas. Ouvre l'application Ollama puis relance ce script."
    }

    foreach ($model in @("llama3", "nomic-embed-text")) {
        $installed = $models | Where-Object {
            $_.name -eq "$model`:latest" -or $_.name -eq $model
        }
        if (-not $installed) {
            Write-Host "Telechargement du modele $model (une seule fois)..."
            & $ollamaCommand.Source pull $model
            if ($LASTEXITCODE -ne 0) {
                throw "Le telechargement de $model a echoue."
            }
            $models = Get-OllamaModels
        }
    }

    if ($InstallOnly) {
        Write-Host "Installation terminee. Relance le script sans -InstallOnly pour ouvrir le chatbot." -ForegroundColor Green
        exit 0
    }

    Write-Host "Le chatbot demarre. Ouvre le lien local affiche par Streamlit dans ton navigateur." -ForegroundColor Green
    & $venvPython -m streamlit run (Join-Path $repositoryRoot "src\web_app.py") --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
    if ($LASTEXITCODE -ne 0) {
        throw "Le serveur web s'est arrete avec une erreur."
    }
}
catch {
    Write-Host ""
    Write-Host "Le chatbot n'a pas pu demarrer : $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
