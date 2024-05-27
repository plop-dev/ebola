@echo off
winget list --id Cloudflare.cloudflared > check.txt
C:\Windows\System32\find.exe /c "Cloudflare.cloudflared" < check.txt > nul
if %errorlevel% equ 0 (
    echo y
) else (
    echo n
)
del check.txt
