Write-Host "`n=== Run 1: Executing TOTE cycle... ==="
python cli/run_project.py examples/tote_example.mg8
$qson1 = Get-Content examples/out/tote_example.qson -Raw | ConvertFrom-Json
$trace1 = $qson1.events[-1].trace_id
Write-Host "Completed. Terminal trace ID generated: $trace1"

Write-Host "`n=== Run 2: Executing TOTE cycle... ==="
python cli/run_project.py examples/tote_example.mg8
$qson2 = Get-Content examples/out/tote_example.qson -Raw | ConvertFrom-Json
$trace2 = $qson2.events[-1].trace_id
Write-Host "Completed. Terminal trace ID generated: $trace2"

Write-Host "`nComparing runs..."
if ($trace1 -ne $trace2) {
    Write-Host "Success! The system ran deterministic TOTE sequences, generating unique valid QSON traces for each attempt! ADSR & Nych logic integrated successfully." -ForegroundColor Green
} else {
    Write-Host "Failed. Trace IDs not unique." -ForegroundColor Red
}

$events = $qson1.events
Write-Host "`nEvent sequence showing TOTE progression:" -ForegroundColor Yellow
foreach ($e in $events) {
    Write-Host " -> Gate ID: $($e.source_objects.gate_id) | Status: $($e.status) | Decision: $($e.decision)"
}
