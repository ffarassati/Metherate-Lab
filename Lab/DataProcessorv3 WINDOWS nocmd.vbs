Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c DataProcessorv3.bat"
oShell.Run strArgs, 0, false