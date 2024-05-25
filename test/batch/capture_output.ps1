# Start your script as a background job
Start-Job -ScriptBlock { & "C:\Users\realr\Documents\Dev\Projects\wence\test\batch\output.bat" } -Name MyScriptJob

# Wait for 3 seconds
Start-Sleep -Seconds 3

# Capture job output
$jobOutput = Get-Job -Name MyScriptJob | Receive-Job

# Write output to a file
$jobOutput.Content | Out-File -FilePath "C:\Users\realr\Documents\Dev\Projects\wence\test\batch\output.txt" -Append

# (Optional) Stop the running script (if desired)
Stop-Job -Name MyScriptJob
