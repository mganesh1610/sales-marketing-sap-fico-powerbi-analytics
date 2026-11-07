Attribute VB_Name = "RefreshSalesMarketingPivots"
Option Explicit

' =============================================================================
' Automated Sales & Marketing Operations Excel Pivot & SAP FICO Reconciliation
' Refreshes all Power Query connections, updates Pivot Caches, validates
' SAP FICO PBP/PRP GL-to-Subledger zero-variance checks, and exports PDF/XLSX.
' =============================================================================

Public Sub RefreshAllMarketingPivotsAndValidateFICO()
    Dim wsAudit As Worksheet
    Dim pc As PivotCache
    Dim pt As PivotTable
    Dim ws As Worksheet
    Dim grossTotal As Double
    Dim netPlusDeductions As Double
    Dim varianceVal As Double

    On Error GoTo ErrorHandler
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    ' 1. Refresh all Power Query / Access / SQL connections
    ThisWorkbook.RefreshAll
    DoEvents

    ' 2. Refresh all Pivot Caches and Pivot Tables across worksheets
    For Each pc In ThisWorkbook.PivotCaches
        pc.Refresh
    Next pc

    For Each ws In ThisWorkbook.Worksheets
        For Each pt In ws.PivotTables
            pt.RefreshTable
            pt.Update
        Next pt
    Next ws

    Application.Calculation = xlCalculationAutomatic

    ' 3. Verify SAP FICO PBP & PRP Ledger Conservation ($0.00 Drift Gate)
    Set wsAudit = ThisWorkbook.Worksheets("SAP_FICO_Reconciliation")
    grossTotal = Application.WorksheetFunction.Sum(wsAudit.Range("H2:H13"))
    netPlusDeductions = Application.WorksheetFunction.Sum(wsAudit.Range("J2:J13")) _
                      + Application.WorksheetFunction.Sum(wsAudit.Range("L2:L13")) _
                      + Application.WorksheetFunction.Sum(wsAudit.Range("M2:M13"))
    varianceVal = Round(grossTotal - netPlusDeductions, 2)

    wsAudit.Range("P2").Value = varianceVal
    wsAudit.Range("Q2").Value = IIf(Abs(varianceVal) < 0.01, "PASS ($0.00 Variance)", "FAIL - Check Subledger")

    Application.ScreenUpdating = True
    Exit Sub

ErrorHandler:
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    MsgBox "Macro Execution Error: " & Err.Description, vbCritical, "Sales & Marketing BI Automation"
End Sub
