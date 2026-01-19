# Setup Windows Task Scheduler for fault.watch Auto Generator
# Run this script as Administrator in PowerShell

$ScriptPath = "C:\Users\ghlte\projects\fault-watch\scripts"
$PythonPath = "python"  # Or full path like "C:\Users\ghlte\AppData\Local\Programs\Python\Python311\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "fault.watch Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Task 1: Morning Generation (9:30 AM)
Write-Host "Creating Morning Task (9:30 AM)..." -ForegroundColor Yellow
$MorningAction = New-ScheduledTaskAction -Execute $PythonPath -Argument "auto_generator.py --once" -WorkingDirectory $ScriptPath
$MorningTrigger = New-ScheduledTaskTrigger -Daily -At "09:30"
$MorningSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName "FaultWatch-Morning" -Action $MorningAction -Trigger $MorningTrigger -Settings $MorningSettings -Description "fault.watch morning content generation" -Force
    Write-Host "  OK: Morning task created" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 2: Afternoon Generation (4:00 PM)
Write-Host "Creating Afternoon Task (4:00 PM)..." -ForegroundColor Yellow
$AfternoonAction = New-ScheduledTaskAction -Execute $PythonPath -Argument "auto_generator.py --once" -WorkingDirectory $ScriptPath
$AfternoonTrigger = New-ScheduledTaskTrigger -Daily -At "16:00"
$AfternoonSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName "FaultWatch-Afternoon" -Action $AfternoonAction -Trigger $AfternoonTrigger -Settings $AfternoonSettings -Description "fault.watch afternoon content generation" -Force
    Write-Host "  OK: Afternoon task created" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 3: Evening Generation (9:00 PM)
Write-Host "Creating Evening Task (9:00 PM)..." -ForegroundColor Yellow
$EveningAction = New-ScheduledTaskAction -Execute $PythonPath -Argument "auto_generator.py --once" -WorkingDirectory $ScriptPath
$EveningTrigger = New-ScheduledTaskTrigger -Daily -At "21:00"
$EveningSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName "FaultWatch-Evening" -Action $EveningAction -Trigger $EveningTrigger -Settings $EveningSettings -Description "fault.watch evening content generation" -Force
    Write-Host "  OK: Evening task created" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 4: Alert Monitor (runs every 5 minutes during market hours)
Write-Host "Creating Alert Monitor Task (every 5 min, 9AM-5PM)..." -ForegroundColor Yellow
$MonitorAction = New-ScheduledTaskAction -Execute $PythonPath -Argument "auto_generator.py --once" -WorkingDirectory $ScriptPath

# Create trigger for every 5 minutes
$MonitorTrigger = New-ScheduledTaskTrigger -Once -At "09:00" -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Hours 8)
$MonitorSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

try {
    Register-ScheduledTask -TaskName "FaultWatch-AlertMonitor" -Action $MonitorAction -Trigger $MonitorTrigger -Settings $MonitorSettings -Description "fault.watch alert monitoring during market hours" -Force
    Write-Host "  OK: Alert monitor task created" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created tasks:" -ForegroundColor White
Write-Host "  - FaultWatch-Morning     (9:30 AM daily)" -ForegroundColor Gray
Write-Host "  - FaultWatch-Afternoon   (4:00 PM daily)" -ForegroundColor Gray
Write-Host "  - FaultWatch-Evening     (9:00 PM daily)" -ForegroundColor Gray
Write-Host "  - FaultWatch-AlertMonitor (every 5 min, 9AM-5PM)" -ForegroundColor Gray
Write-Host ""
Write-Host "To view tasks: Get-ScheduledTask | Where-Object {`$_.TaskName -like 'FaultWatch*'}" -ForegroundColor Yellow
Write-Host "To remove tasks: Unregister-ScheduledTask -TaskName 'FaultWatch-Morning' -Confirm:`$false" -ForegroundColor Yellow
Write-Host ""
Write-Host "Content will be saved to: C:\Users\ghlte\projects\fault-watch\content-library\" -ForegroundColor Cyan
