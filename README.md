# ebola

```txt
░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░       ░▒▓██████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓██████▓▒░ ░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓████████▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░ 
```

## installing

1. the `installer.bat(.exe)` script
    - user downloads `installer.bat(.exe)` **only**.
    - the installer is now in the `C:\Users\\[user]\Downloads` folder
2. running the installer
    - will ask for admin (UAC prompt opens)
    - move all the checkers (`ch[number].bat`) and ebola (folder) to `C:\Windows\System32`
    - move `FpsUnlocker.exe` to `C:\Program Files`
    - run `ebola.bat(.exe)`

## the `ebola.bat(.exe)` script

1. run `shareport.bat`
    - will ask for admin (UAC)
    - will open cmd but minimised (*make it run in tray?*)
    - run `getporturl.pyw` with pythonw so it runs in background
    - url gets generated then sent to webserver via `/control/url/[id]`
    - control url of the `[id]` gets updated automatically
2. run `main.py(.pyw)`
    - we all know what the main file does

## notices

- make sure info.txt has an `id` and `url` property that isn't empty
- make sure webserver is running when commands executed to mitigate errors
