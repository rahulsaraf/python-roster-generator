import os
import re
import sys
from pandas.core.frame import DataFrame
import wx
from wx.lib import sheet
import wx.lib.filebrowsebutton
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import pandas as pd
from calendar import week
from StringIO import StringIO


class spreadsheet(sheet.CSheet):
    
    flframe = pd.DataFrame()

    def __init__(self, parent):
        sheet.CSheet.__init__(self, parent)
        self.row = self.col = 0
        self.SetNumberRows(1000)
        self.SetNumberCols(25)
        for i in range(1000):
            self.SetRowSize(i, 20)

    def OnGridSelectCell(self, event):
        self.row, self.col = event.GetRow(), event.GetCol()
        control = self.GetParent().GetParent().position
        value =  self.GetColLabelValue(self.col) + self.GetRowLabelValue(self.row)
        control.SetValue(value)
        event.Skip()
        
    def OnLoadSpreadsheet(self, week, club, columns, filename):
        self.myframe =  self.getList(week,  club, colList=columns, filename=filename)
        tcolumns = self.myframe.columns
        for col in range(len(tcolumns)):
            self.SetCellValue( 0,col, tcolumns[col])
            self.SetColSize(col, len(tcolumns[col]) * 6) 
        i = 0
        self.finDataframe.columns = tcolumns;
        for row in self.myframe.iterrows():
            i = i + 1
            for col in range(len(tcolumns)):
                self.SetCellValue( i,col, str(row[1][col]))
        return
    
    def getListForAll(self, weekList, campList, filename, columns,allWeeks=False):
        i = 0
       
        for week in weekList:
            campsList =  example.getCamps(week) if allWeeks else campList
            for camp in campsList:
                newFrame = self.getList(week,  camp, colList=columns, filename=filename)
                tcolumns = newFrame.columns
                for col in range(len(tcolumns)):
                    self.SetCellValue( i,col, tcolumns[col])
                    self.SetColSize(col, len(tcolumns[col]) * 6)
                for row in newFrame.iterrows():
                    i = i + 1
                    for col in range(len(tcolumns)):
                        self.SetCellValue( i,col, str(row[1][col]))
                i = i + 2
                newFrame.loc[i] = tcolumns
                self.flframe = self.flframe.append(newFrame)
            i = i + 1
        return    
            
    def getList(self,week, club, colList, filename):
        s = pd.read_csv(filename)
        df2 = DataFrame(s)
        df3 = DataFrame(s)
        
        columns = df2.columns
        xlist = list()
        for c in columns:
            if c.upper().find("PRICE ADJUSTMENT") == -1:
                if  c.find(week) != -1:
                    xlist.append(str(c))
                        
        indexList = list()
        for xcolumn in xlist:
            colist = list()
            colist.append(xcolumn)
            df4 = DataFrame(df3, columns=colist)[~df3[xcolumn].isnull()]
            for row in df4.iterrows():
                if row[1][0] == club:
                    indexList.append(row[0])
        fin = DataFrame(df2, index=indexList, columns=colList)
        if fin.empty:
            return
        fin["Camp"] = club
        fin["Week"] = week
        return fin


class spreadsheetFrame(wx.Frame):
    week = str()
    club = str()
    columnsSel = list()
    filename = str()
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title)

        box = wx.BoxSizer(wx.VERTICAL)
        
        toolbar2 = wx.ToolBar(self, wx.TB_HORIZONTAL | wx.TB_TEXT)
        self.position = wx.TextCtrl(toolbar2)
        back_button = wx.Button(toolbar2, -1, "Back <-")
        self.Bind(wx.EVT_BUTTON, self.OnBack, back_button)
        
        download_button = wx.Button(toolbar2, -1, "DownLoad File")
        self.Bind(wx.EVT_BUTTON, self.OnDownload, download_button)
        toolbar2.AddControl(self.position)
        toolbar2.AddControl(back_button)
        toolbar2.AddControl(download_button)
        
        toolbar2.AddSeparator()
        box.Add(toolbar2)
        box.Add((5,10) , 0)

        toolbar2.Realize()
        self.SetSizer(box)
        notebook = wx.Notebook(self, -1, style=wx.RIGHT)

        self.sheet1 = spreadsheet(notebook)
        self.sheet1.SetFocus()

        notebook.AddPage(self.sheet1, 'Sheet1')
        box.Add(notebook, 1, wx.EXPAND)

        self.CreateStatusBar()
        self.Centre()
        self.Show(True)
        self.Maximize(True)

    def OnDownload(self, event):
        #self.sheet1.flframe =  self.sheet1.getList(week=self.week,club=self.club, colList=self.columnsSel, filename=self.filename)        
        wcd='All files(*)|*|CSV files (*.csv)|*.csv'
        dir = os.getcwd()
        save_dlg = wx.FileDialog(self, message='Save file as...', defaultDir=dir, defaultFile='',
                        wildcard=wcd, style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if save_dlg.ShowModal() == wx.ID_OK:
            path = save_dlg.GetPath()

            try:
                self.sheet1.flframe.to_csv(path, sep=',', encoding='utf-8')
                self.modify = False

            except IOError, error:
                dlg = wx.MessageDialog(self, 'Error saving file\n' + str(error))
                dlg.ShowModal()
        save_dlg.Destroy()
        return
    
    def OnBack(self, event):
        self.Show(False)
        example.Show(True)

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, 1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class mainframe(wx.Frame):

    filename = str()
    weekList = list()
    camplist = list()
    packages = list()
    columnsSelect = list()
    week = str()
    club = str()
    def __init__(self, parent, title):    
        super(mainframe, self).__init__(parent, title=title)
        
        self.InitUI()
        self.Centre()
        self.Maximize(True)

    def InitUI(self):
      
        panel = wx.Panel(self)
        
        sizer = wx.GridBagSizer(10, 5)

        text1 = wx.StaticText(panel, label="CS Out-reach Roster Generator")
        sizer.Add(text1, pos=(0, 0),span=(1, 3),  flag=wx.TOP|wx.LEFT|wx.BOTTOM, 
            border=15)


        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5), 
            flag=wx.EXPAND|wx.BOTTOM, border=10)

        self.fbb = wx.lib.filebrowsebutton.FileBrowseButton(panel,
            labelText="Select a CSV file:   ", fileMask="*.csv")
        

        sizer.Add(self.fbb, pos=(2, 0), span=(1, 4), flag=wx.TOP|wx.EXPAND, 
            border=5)

        load_button = wx.Button(panel, -1, "Load File")
        self.Bind(wx.EVT_BUTTON, self.OnLoadFile, load_button)
        #button1 = wx.Button(panel, label="Browse...")
        sizer.Add(load_button, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5)
        
        
        

        text4 = wx.StaticText(panel, label="Select Week    :-")
        sizer.Add(text4, pos=(3, 0), flag=wx.TOP|wx.LEFT, border=10)

        self.combo1 = wx.ComboBox(panel,value="None",choices=self.weekList)
        sizer.Add(self.combo1, pos=(3, 1), span=(1, 3), 
            flag=wx.TOP|wx.EXPAND, border=5)

        button2 = wx.Button(panel, label="Load Camps")
        self.Bind(wx.EVT_BUTTON, self.loadCamps, button2)
        sizer.Add(button2, pos=(3, 4), flag=wx.TOP|wx.RIGHT, border=5)



        text5 = wx.StaticText(panel, label="Select Camps :-")
        sizer.Add(text5, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)

        self.combo2 = wx.ComboBox(panel,value="None",choices=self.camplist)
        sizer.Add(self.combo2, pos=(4, 1), span=(1, 3), 
            flag=wx.TOP|wx.EXPAND, border=5)

        self.list = CheckListCtrl(panel)
        sizer.Add(self.list, pos=(5, 1), flag=wx.TOP|wx.RIGHT, border=5)
        
        self.apply = wx.Button(panel, -1, 'Apply')
        self.Bind(wx.EVT_BUTTON, self.OnApply,self.apply )
        sizer.Add(self.apply, pos=(5, 2), flag=wx.TOP|wx.RIGHT, border=5)
        
        self.log = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE,size=(569, 150))
        #self.log.Size.SetWidth(800)
        sizer.Add(self.log, pos=(6, 1), flag=wx.TOP|wx.RIGHT, border=5)
        
        self.check1 = wx.CheckBox(panel, -1, "Generate Roster for all Camps for selected week")
        sizer.Add(self.check1, pos=(7, 1), flag=wx.TOP|wx.RIGHT, border=5)

        self.check2 = wx.CheckBox(panel, -1, "Generate Roster for all Camps for all weeks(This will take 1-2 minutes to generate)")
        sizer.Add(self.check2, pos=(8, 1), flag=wx.TOP|wx.RIGHT, border=5)

        self.next = wx.Button(panel, -1, 'Next')
        self.Bind(wx.EVT_BUTTON, self.OnNext,self.next )
        sizer.Add(self.next, pos=(8, 2), flag=wx.TOP|wx.RIGHT, border=5)

        
        self.list.InsertColumn(0, 'Select Columns', width=567)
    
        for i in self.packages:
            self.list.InsertStringItem(sys.maxint, i[0])

        sizer.AddGrowableCol(2)
        
        panel.SetSizer(sizer)
        self.Show(True)

    def OnLoadFile(self, evt):
        self.filename = self.fbb.GetValue()
        self.weekList = self.getWeeks(filename=self.filename)
        self.combo1.AppendItems(self.weekList)
        self.combo1.SetSelection(0)
        self.camplist = self.getCamps(week=self.weekList[0])
        self.combo2.AppendItems(self.camplist)
        self.combo2.SetSelection(0)
        self.packages = self.getColumns()
        for i in self.packages:
            index = self.list.InsertStringItem(sys.maxint, i)
        return
        
    def getWeeks(self, filename):
        if not filename:
            return 
        s = pd.read_csv(filename)
        df2 = DataFrame(s)
        columns = df2.columns
        
        x = set()
        xlist = list()
        for c in columns:
            if c.upper().find("PRICE ADJUSTMENT") == -1:
                    if  c.upper().find("CAMPS:") != -1:
                        x.add(re.split("\.?", str(c))[0])                
        
        for x1 in x: xlist.append(x1)
        xlist.sort(cmp=None, key=None, reverse=False)    
        return xlist
    
    def loadCamps(self, evt):
        self.camplist = self.getCamps(week=self.weekList[self.combo1.GetCurrentSelection()])
        self.combo2.SetItems(self.camplist)
        self.combo2.SetSelection(0)
        return
    
    def OnNext(self,evt):
        self.sheetN = spreadsheetFrame(None, -1, 'SpreadSheet')
        self.sheetN.week = self.weekList[self.combo1.GetCurrentSelection()]
        self.sheetN.club = self.camplist[self.combo2.GetCurrentSelection()]
        self.sheetN.columnsSel = self.columnsSelect
        self.sheetN.filename = self.filename
        
        nweeklist = list()
        nweeklist.append(self.sheetN.week)
        ncamplist = list()
        ncamplist.append(self.sheetN.club)
        
        if self.check2.Value == True:
            self.sheetN.sheet1.getListForAll(weekList=self.weekList, campList=self.camplist, filename=self.filename, columns=self.columnsSelect, allWeeks=True)
        elif self.check2.Value == False and self.check1.Value == True:
            self.sheetN.sheet1.getListForAll(weekList=nweeklist, campList=self.camplist, filename=self.sheetN.filename, columns=self.sheetN.columnsSel,allWeeks=False)
        else :
            self.sheetN.sheet1.getListForAll(weekList=nweeklist, campList=ncamplist,filename=self.sheetN.filename, columns=self.sheetN.columnsSel, allWeeks=False)
        
        self.Show(False)
        self.sheetN.Show(True)
        return
    def getCamps(self,week):
        s = pd.read_csv("D:/UTDallasStudy/summer.csv")
        df2 = DataFrame(s)
        df3 = DataFrame(s)
        
        columns = df2.columns
        x = set()
        xlist = list()
        ylist = list()
        for c in columns:
            if c.upper().find("PRICE ADJUSTMENT") == -1:
                if  c.find(week) != -1:
                    x.add(re.split("\.?", str(c))[0])
                    ylist.append(c)
                else:
                    x.add(str(c))
                    
        for x1 in x: xlist.append(x1)
        xlist.sort(cmp=None, key=None, reverse=False)
        campset = set()
        for y in ylist:
            clist = list()
            clist.append(y)
            res = DataFrame(df3, columns=clist)[~df3[y].isnull()]
            for row in res.iterrows():
                campName = row[1][0]
                campset.add(campName)
        camplist = list()
        for camp in campset: camplist.append(camp)
        camplist.sort(cmp=None, key=None, reverse=False)
        return camplist
    
    def getColumns(self):
        s = pd.read_csv(self.filename)
        df2 = DataFrame(s)
        columns = df2.columns
        x = set()
        xlist = list()
        for c in columns:
            if c.upper().find("PRICE ADJUSTMENT") == -1:
                if (c.upper().find("CAMPS:") == -1):
                    x.add(str(c))
                    
        for x1 in x: xlist.append(x1)
        xlist.sort(cmp=None, key=None, reverse=False)
        return xlist
    
    
    def OnApply(self, event):
        num = self.list.GetItemCount()
        self.columnsSelect = list()
        for i in range(num):
            if i == 0: self.log.Clear()
            if self.list.IsChecked(i):
                self.log.AppendText(self.list.GetItemText(i) + '\n')
                self.columnsSelect.append(self.list.GetItemText(i))
        
if __name__ == '__main__':
    app = wx.App()
    example = mainframe(None, title="CS Outreach Roster Generator")
    app.MainLoop()