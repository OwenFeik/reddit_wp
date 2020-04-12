Set objShell = CreateObject("Wscript.Shell")
strScriptPath = Wscript.ScriptFullName
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.GetFile(strScriptPath)
strFolder = objFSO.GetParentFolderName(objFile)
strCommand = "python " & """" & strFolder & "\reddit_wp.py"""
objShell.Run strCommand, 0
