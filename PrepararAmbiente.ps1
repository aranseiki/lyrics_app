Clear-Host

# PARA GARANTIR A LEITURA DE ACENTUAÇÕES E CODIGOS ESPECIAIS | 1252 ANSI | 65001 UTF8
chcp 65001

Write-Host `n 'Iniciando a preparação de ambiente' `n

Write-Host 'Coletando o diretório de trabalho' `n
$DiretorioRaiz = Split-Path -parent $MyInvocation.MyCommand.Path

$DiretorioConfig = $DiretorioRaiz + '\ConfigPowerShell.ini'
$ConteudoArquivoIni = Get-Content $DiretorioConfig

[Collections.ArrayList] $ListaParametrosIni = @()
foreach($Linha in $ConteudoArquivoIni) {
    $TextoConvertido = ConvertFrom-StringData -StringData $Linha
    $ListaParametrosIni.Add($TextoConvertido) | Out-Null
}

Write-Host 'Dados coletados: ' `n
$VersaoPython = $ListaParametrosIni.Versao
$NomeVenv = $ListaParametrosIni.NomeVenv
$CaminhoArquivoRequirements = $ListaParametrosIni.CaminhoArquivoRequirements
$NomeArquivoRequirements = $ListaParametrosIni.NomeArquivoRequirements
$Proxy = $ListaParametrosIni.Proxy

Write-Host 'Coletando o caminho do requirements' `n
if (
    [string]::IsNullOrEmpty($CaminhoArquivoRequirements) -or
    [string]::IsNullOrWhiteSpace($CaminhoArquivoRequirements) -or
    $CaminhoArquivoRequirements -eq "''" -or
    $CaminhoArquivoRequirements -eq '""'
) {
    $CaminhoArquivoRequirements = $DiretorioRaiz
} else {
    $CaminhoArquivoRequirements = $CaminhoArquivoRequirements.Trim('"')
    $CaminhoArquivoRequirements = $CaminhoArquivoRequirements.Trim("'")
}

Write-Host 'Coletando o nome do requirements' `n
if (
    [string]::IsNullOrEmpty($NomeArquivoRequirements) -or
    [string]::IsNullOrWhiteSpace($NomeArquivoRequirements) -or
    $NomeArquivoRequirements -eq "''" -or
    $NomeArquivoRequirements -eq '""'
) {
    $NomeArquivoRequirements = '\requirements.txt'
} else {
    $NomeArquivoRequirements = $NomeArquivoRequirements.Trim('"')
    $NomeArquivoRequirements = $NomeArquivoRequirements.Trim("'")
}

Write-Host 'Montando o caminho do arquivo requirements' `n
[string] $CaminhoCompletoArquivoRequirements = 
    $CaminhoArquivoRequirements, $NomeArquivoRequirements -join '\'

Write-Host 'Definindo configurações do Python' `n
[string] $CaminhoPython = ''
if ( $VersaoPython -ne '' ) {
    Write-Host 'Versão definida à mão: ' $VersaoPython `n
    $ListaCaminhoPython = Get-ChildItem ${env:ProgramFiles(x86)} -Filter *$VersaoPython*
    if ([string]::IsNullOrEmpty($ListaCaminhoPython)) {
        $ListaCaminhoPython = Get-ChildItem ${env:ProgramFiles} -Filter *$VersaoPython*
    }
    if ([string]::IsNullOrEmpty($ListaCaminhoPython)) {
        $AppDataLocal = $env:LOCALAPPDATA
        $AppDataLocal = $AppDataLocal + '\Programs\Python'
        $ListaCaminhoPython = Get-ChildItem $AppDataLocal -Filter *$VersaoPython*
    }
} else {
    foreach ($LinhaEnv in $env:Path) {
        $LinhaEnv = $LinhaEnv.split(';')
        foreach ($env in $LinhaEnv) {
            if (
                ($env.ToUpper().Contains('PYTHON')) -or
                ($env.ToUpper().Contains('ANACONDA'))
                ) {
                $CaminhoPython = $env
            }
        }
    }
    Write-Host 'Versão automática: ' $CaminhoPython `n    
}

try {
    $CaminhoPython = $ListaCaminhoPython[$ListaCaminhoPython.Rank].FullName
} catch {
    $CaminhoPython = $ListaCaminhoPython.FullName
}

$ExecutavelPythonGlobal = $CaminhoPython + '\python.exe'

Write-Host 'Definindo configurações do ambiente virtual' `n
$ExecutavelPythonVEnv = $DiretorioRaiz + '\' + $NomeVenv + '\Scripts\python.exe'
$CaminhoEnv = $DiretorioRaiz + '\' + $NomeVenv

Write-Host 'Criando o ambiente virtual' `n
Set-Location -Path $DiretorioRaiz
& $ExecutavelPythonGlobal -m venv $CaminhoEnv

Write-Host 'Ativando o ambiente virtual' `n
$ArquivoActivate = $DiretorioRaiz + '\' + $NomeVenv + '\Scripts\Activate.ps1'
& $ArquivoActivate

if (
    [string]::IsNullOrEmpty($Proxy) -or
    [string]::IsNullOrWhiteSpace($Proxy) -or
    $Proxy -eq "''" -or
    $Proxy -eq '""'
) {
    Write-Host 'Atualizando o pip' `n
    Write-Host 'Sem proxy' `n
    & $ExecutavelPythonVEnv -m pip install --trusted-host artifactory.produbanbr.corp --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip

    Write-Host `n 'Instalando as dependências' `n
    & $ExecutavelPythonVEnv -m pip install --trusted-host artifactory.produbanbr.corp --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $CaminhoCompletoArquivoRequirements
} else {
    Write-Host 'Atualizando o pip' `n
    Write-Host 'Com proxy' `n

    $Proxy = $Proxy.Replace('"', '').Replace("'", "")
    & $ExecutavelPythonVEnv -m pip install --trusted-host artifactory.produbanbr.corp --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip --proxy $Proxy

    Write-Host `n 'Instalando as dependências' `n
    & $ExecutavelPythonVEnv -m pip install --trusted-host artifactory.produbanbr.corp --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $CaminhoCompletoArquivoRequirements --proxy $Proxy
}

Write-Host `n 'Preparação de ambiente finalizada' `n
