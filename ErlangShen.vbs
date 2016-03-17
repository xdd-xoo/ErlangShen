Function WatertownGUI
    Dim pathLevel, metaType, dutType, logPath
    blnValid = False
    
    ' Create an IE object
    Set objIE = CreateObject( "InternetExplorer.Application" )
    ' specify some of the IE window's settings
    objIE.Navigate "about:blank"
    objIE.Document.Title = "ErlangShen v1.0"
    objIE.ToolBar        = False
    objIE.Resizable      = False
    objIE.StatusBar      = False
    objIE.Width          = 800
    objIE.Height         = 350
    ' Center the dialog window on the screen
    'With objIE.Document.ParentWindow.Screen
    '    objIE.Left = (.AvailWidth  - objIE.Width ) \ 2
    '    objIE.Top  = (.Availheight - objIE.Height) \ 2
    'End With
    ' Wait till IE is ready
    Do While objIE.Busy
        WScript.Sleep 200
    Loop
    
    ' Insert the HTML code to prompt for user input
    objIE.Document.Body.InnerHTML = "<DIV ALIGN=""CENTER"">" _
              & "<TABLE CELLSPACING=""5"">" _
              & "<TR NOWRAP><TH COLSPAN=""2"" STYLE=""font-size:1.5em"">" _
              & "ErLangShen Parameters" _
              & "</TH></TR>" _
              & "<TR NOWRAP><TH COLSPAN=""2"" STYLE=""BORDER-BOTTOM: 1px solid #CFCFCF;color:red"">" _
              & "</TH></TR>" _
              & "<TR NOWRAP><TD>Throttle:</TD>" _
              & "<TD><SELECT ID=""throttle"" STYLE=""width:200px;"">" _
              & "<OPTION VALUE=1000>1000</OPTION>" _
              & "<OPTION VALUE=500 SELECTED>500</OPTION></SELECT><small>*500=500ms,1000=1000ms</small></TD></TR>" _
              & "<TR NOWRAP><TD>Event Count:</TD>" _
              & "<TD><SELECT ID=""eventCount"" STYLE=""width:200px;"">" _
              & "<OPTION VALUE=600 SELECTED>600</OPTION>" _
              & "<OPTION VALUE=1200>1200</OPTION></SELECT><small>*Monkey Test Event Number</small></TD></TR>" _
              & "<TR NOWRAP><TD>Monkey</TD>" _
              & "<TD><SELECT ID=""monkey"" STYLE=""width:200px;"">" _
              & "<OPTION VALUE=""No"">No</OPTION>" _
              & "<OPTION VALUE=""Yes"" SELECTED>Yes</OPTION></SELECT></TD></TR>" _
              & "<TR NOWRAP><TD VALIGN=""TOP"">APP Path:</TD>" _
              & "<TD><INPUT TYPE=""TEXT"" STYLE=""width:600px;"" " _
              & "ID=""appPath""></TEXTAREA></TD></TR>" _
              & "</TABLE>" _
              & "<P><INPUT TYPE=""hidden"" ID=""OK"" " _
              & "NAME=""OK"" VALUE=""0"">" _
              & "<INPUT TYPE=""submit"" VALUE="" RUN "" " _
              & "OnClick=""VBScript:OK.Value=1"" STYLE=""WIDTH:200px;HEIGHT:50px;CURSOR:POINTER;""></P><P STYLE=""font:normal 0.75em Arial;color:#CFCFCF"">Powered by PDT.CHINA.TDA</P></DIV>"
    ' Make the window visible
    objIE.Visible = True
    
    ' Wait for valid input (2 non-empty equal passwords)
    Do Until blnValid = True
        ' Wait till the OK button has been clicked
        On Error Resume Next
        Do While objIE.Document.All.OK.Value = 0
            WScript.Sleep 200
            If Err Then
                WatertownGUI = Array( "", "" )
                objIE.Quit
                Set objIE = Nothing
                Exit Function
            End If
        Loop
        On Error Goto 0
        ' Read the user input from the dialog window
        params = Array( objIE.Document.All.throttle.Value, _
                        objIE.Document.All.eventCount.Value, _
                        objIE.Document.All.monkey.Value, _
                        objIE.Document.All.appPath.Value )
        ' Check if the new password and confirmed password match
        If params(3) = "" Then
            MsgBox "Log path cannot be empty", _
                   vbOKOnly + vbInformation + vbApplicationModal, _
                   "Please input log path!"
            objIE.Document.All.OK.Value              = 0
        Else
            blnValid = True
        End If
    Loop
    ' Close and release the object
    objIE.Quit
    Set objIE = Nothing
    ' Return the passwords in an array
    WatertownGUI = params
End Function

params = WatertownGUI
If UBound(params) >= 3 Then
    Set wss=createobject("wscript.shell")
    wss.run "ErlangShen.bat """& params(0)&""" """&params(1)&""" """&params(2)&""" """&params(3)&""""
End If