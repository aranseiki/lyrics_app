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
$NomeVenv = $ListaParametrosIni.NomeVenv

Write-Host 'Coletando o diretório do ambiente virtual' `n
$NomeVenv = $NomeVenv.trim('"')
$NomeVenv = $NomeVenv.trim("'")
$DiretorioVEnv = $DiretorioRaiz, $NomeVenv -join '\'

Write-Host "Definindo o diretório de contexto" `n
Set-Location -Path $DiretorioRaiz

Write-Host "Finalizando processos" `n
Import-Module .\parar.ps1

try {
    Write-Host 'Desativando o ambiente virtual' `n
    Deactivate
} catch {
    Out-Null
}

Write-Host 'Removendo o ambiente' `n
Remove-Item -Path $DiretorioVEnv -Recurse -Force -ErrorAction SilentlyContinue

Write-Host 'Limpeza de ambiente finalizada' `n
