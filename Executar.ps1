Clear-Host

# PARA GARANTIR A LEITURA DE ACENTUAÇÕES E CODIGOS ESPECIAIS | 1252 ANSI | 65001 UTF8
chcp 65001

Write-Host `n 'Iniciando a execução do fluxo de trabalho' `n

Write-Host 'Coletando o diretório de trabalho' `n
$ArquivoScript = $MyInvocation.MyCommand.Path
$DiretorioRaiz = Split-Path -parent $ArquivoScript

$DiretorioConfig = $DiretorioRaiz + '\ConfigPowerShell.ini'
$ConteudoArquivoIni = Get-Content $DiretorioConfig

[Collections.ArrayList] $ListaParametrosIni = @()
foreach($Linha in $ConteudoArquivoIni) {
    $TextoConvertido = ConvertFrom-StringData -StringData $Linha
    $ListaParametrosIni.Add($TextoConvertido) | Out-Null
}

Write-Host 'Dados coletados: ' `n
$NomeVenv = $ListaParametrosIni.NomeVenv

Write-Host 'Coletando o diretório de ambiente virtual' `n
$DiretorioVEnv = $DiretorioRaiz + $NomeVenv
$ValidacaoDiretorioVEnv = Test-Path -Path $DiretorioVEnv

Write-Host "Definindo o diretório de contexto" `n
Set-Location -Path $DiretorioRaiz

Write-Host "Finalizando processos para garantir o bom funcionamento do fluxo" `n
$ArquivoPararPS1 = $DiretorioRaiz + '\parar.ps1'
Import-Module $ArquivoPararPS1

if ($ValidacaoDiretorioVEnv -eq $false) {

    Write-Host "Ambiente virtual não encontrado, " -NoNewline
    Write-Host "Criando um ambiente virtual" `n
    $ArquivoPrepararAmbientePS1 = $DiretorioRaiz + '\PrepararAmbiente.ps1'
    Import-Module $ArquivoPrepararAmbientePS1

}

Write-Host 'Verificando quantidade de execuções destinadas: ' `n
$NumeroExecucoes = $ListaParametrosIni.NumeroExecucoes

if (
    ($null -eq $NumeroExecucoes) -or
    ("''" -eq $NumeroExecucoes) -or
    ('""' -eq $NumeroExecucoes) -or
    (' ' -eq $NumeroExecucoes)
) {
    $NumeroExecucoes = '1'
}

$NumeroExecucoes = $NumeroExecucoes.Replace("'", '').Replace('"', '')
$NumeroExecucoes = [int] $NumeroExecucoes
for($execucao = 1; $execucao -le $NumeroExecucoes; $execucao++) {
    Write-Host "Executando o fluxo de trabalho" `n
    Write-Host "Execução $execucao de $NumeroExecucoes" `n

    $ArquivoIniciarPS1 = $DiretorioRaiz + '\iniciar.ps1'
    Import-Module $ArquivoIniciarPS1
}

Write-Host 'Execução do fluxo de trabalho Finalizado' `n

exit