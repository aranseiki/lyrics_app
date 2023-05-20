# PARA GARANTIR A LEITURA DE ACENTUAÇÕES E CODIGOS ESPECIAIS | 1252 ANSI | 65001 UTF8
chcp 65001

Write-Host "Iniciando fluxo de trabalho" `n

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
$NomeVenv = $ListaParametrosIni.NomeVenv
$NomeArquivoPy = $ListaParametrosIni.NomeArquivoPy

Write-Host "Definindo o diretório de contexto" `n
Set-Location -Path $DiretorioRaiz

Write-Host "Definindo parâmetros do ambiente virtual" `n
$NomeVenv = $NomeVenv.trim('"')
$NomeVenv = $NomeVenv.trim("'")
$DiretorioVenv = $DiretorioRaiz, $NomeVenv   -join '\'
$CaminhoActivate = $DiretorioVenv + '\Scripts\Activate.ps1'
Write-Host "Caminho do activate: " $CaminhoActivate `n

Write-Host "Ativando o ambiente virtual" `n
& $CaminhoActivate

Write-Host "Definindo parâmetros do Python" `n
if (
    [string]::IsNullOrEmpty($NomeArquivoPy) -or
    [string]::IsNullOrWhiteSpace($NomeArquivoPy) -or
    $NomeArquivoPy -eq "''" -or
    $NomeArquivoPy -eq '""'
) {
    $NomeArquivoPy = 'main.py'
}

$NomeArquivoPy = $NomeArquivoPy.trim('"')
$NomeArquivoPy = $NomeArquivoPy.trim("'")
$caminhoArquivoMain = ('"' + $DiretorioRaiz), ($NomeArquivoPy + '"')  -join '\'
$ExecutavelPythonVEnv = $DiretorioVenv + '\Scripts\python.exe'
Write-Host "caminhoArquivoMain: " $caminhoArquivoMain

Write-Host `n "Executando o Python chamando o arquivo como parâmetro" `n
start-process $ExecutavelPythonVEnv $caminhoArquivoMain

Write-Host `n 'Fluxo de trabalho finalizado' `n

exit