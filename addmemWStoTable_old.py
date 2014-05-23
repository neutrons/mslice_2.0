def addmemWStoTable(table,wsname,wstype,wssize,wsindex):
    
    #get constants
    const=constants()

    
    if wstype == '':
        wstype = 'unknown'

    saved='No'
    
    #First determine if there is an open row
    #need to determine the available row number in the workspace table
    
    Nrows=table.rowCount()
    print "Nrows: ",Nrows,"  wsindex: ",wsindex

    emptyRowCnt=0
    emptyRows = []
	
    for row in range(Nrows):
        item=str(table.item(row,0)) 
        if item == 'None':
            emptyRowCnt +=1
            emptyRows.append(row)
    print "emptyRows: ",emptyRows,"  emptyRowCnt: ",emptyRowCnt
    if emptyRowCnt != 0:
        #case where there is an empty row to use
        userow=int(emptyRows[0])
        if wsindex != -1:  #check for case where we will replace an existing row in the table
            userow=wsindex

    else:
        #case where a row needs to be added
        userow=Nrows #recall that row indexing starts at zero thus the row to add would be at position Nrows
        if wsindex != 0:  #check for case where we will replace an existing row in the table
            print "Case 0"
            userow=wsindex
            #special case where a single workspace added from workspace manager is becoming a group workspace in WS composer
            if userow == Nrows == 1:
                print "Case 1"
                #case where a row needs to be added to the table 
                print "Adding a row"
                table.insertRow(userow)
            #special case where a single workspace is added via the workspace composer
            if userow == 1 and Nrows == 0:
                print "Case 2"
                #case where a row needs to be added to the table 
                print "Adding a row b"
                userow=0
                table.insertRow(userow)  
            if wsindex > Nrows:
                #case where we'd go past the end of the table so we need to add a row
                userow=wsindex
                table.insertRow(userow)    
        else:
            print "Case not found"            
        if wsindex > 0:  #check if we need to add a row or not
            #case to insert
            table.insertRow(Nrows)
        col=const.WSM_SelectCol
#        addComboboxToWSTCell(table,userow,col)
        addCheckboxToWSTCell(table,userow,col,True)
    
    #now add the row		
    print "userow: ",userow
    table.setItem(userow,const.WSM_WorkspaceCol,QtGui.QTableWidgetItem(wsname)) #Workspace Name 
    table.setItem(userow,const.WSM_TypeCol,QtGui.QTableWidgetItem(wstype)) #Workspace Type
    table.setItem(userow,const.WSM_SavedCol,QtGui.QTableWidgetItem(saved)) #FIXXME Hard coded for now
    table.setItem(userow,const.WSM_SizeCol,QtGui.QTableWidgetItem(wssize)) #Size 
    addCheckboxToWSTCell(table,userow,const.WSM_SelectCol,True)
#    table.setItem(userow,const.WSM_SelectCol,QtGui.QTableWidgetItem('')) #select - will want to change this
