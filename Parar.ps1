# PARA GARANTIR A LEITURA DE ACENTUAÇÕES E CODIGOS ESPECIAIS | 1252 ANSI | 65001 UTF8
chcp 65001

Clear-Host

Write-Host `n "Iniciando o encerramento dos processos" `n

Write-Host 'Coletando o diretório de trabalho' `n
$DiretorioRaiz = Split-Path -parent $MyInvocation.MyCommand.Path

Write-Host "Definindo o diretório de contexto" `n
Set-location $DiretorioRaiz

$DiretorioConfig = $DiretorioRaiz + '\ConfigPowerShell.ini'
$ConteudoArquivoIni = Get-Content $DiretorioConfig

[Collections.ArrayList] $ListaParametrosIni = @()
foreach($Linha in $ConteudoArquivoIni) {
    $TextoConvertido = ConvertFrom-StringData -StringData $Linha
    $ListaParametrosIni.Add($TextoConvertido) | Out-Null
}

Write-Host 'Dados coletados: ' `n
$ListaProcessos = $ListaParametrosIni.Finalizar

if (
    [string]::IsNullOrEmpty($ListaProcessos) -or
    [string]::IsNullOrWhiteSpace($ListaProcessos) -or
    $ListaProcessos -eq "''" -or
    $ListaProcessos -eq '""'
) {
    Out-Null
} else {
    $ListaProcessos = $ListaProcessos.split(',')
    
    ForEach($Processo in $ListaProcessos) {
        
        Write-Host "Encerrando o processo " $Processo.Replace("*", "") `n
        stop-process -Name $Processo
        
    }
    
}

Write-Host 'Encerramento dos processos finalizado' `n

exit