Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c DataProcessorv4.bat"
oShell.Run strArgs, 0, false