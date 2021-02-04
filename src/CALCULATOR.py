from tkinter import *
fields = ('Number of Pictures', 'Time Interval (s)', 'Total Time (min.sec)')

def totaltime(entries):
    if legality(entries) == False:
        print("Illegal characters in entry. Please re-try.")
    else:        
        npics = float(entries['Number of Pictures'].get())
        ntimeint = float(entries['Time Interval (s)'].get())
        totaltime = npics*ntimeint
        totalmin = str(int(totaltime // 60))
        totalsec = str(int(totaltime % 60))
        time = totalmin + "." + totalsec
        entries['Total Time (min.sec)'].delete(0, END)
        entries['Total Time (min.sec)'].insert(0, time)
        print("Total Time: " + totalmin + " min " + totalsec + " sec")   

def timeint(entries):
    if legality(entries) == False:
        print("Illegal characters in entry. Please re-try.")
    else:        
        npics = float(entries['Number of Pictures'].get())
        tottime = float(entries['Total Time (min.sec)'].get())
        minutes = int(tottime)
        seconds = int((tottime % 1) * 100)
        totaltime = minutes*60 + seconds
        ntimeint = totaltime/npics
        entries['Time Interval (s)'].delete(0, END)
        entries['Time Interval (s)'].insert(0, ntimeint)
        print("Time Interval: %f" % ntimeint, " seconds")

def totpics(entries):
    if legality(entries) == False:
        print("Illegal characters in entry. Please re-try.")
    else:        
        ntimeint = float(entries['Time Interval (s)'].get())
        tottime = float(entries['Total Time (min.sec)'].get())
        minutes = int(tottime)
        seconds = int((tottime % 1) * 100)
        totaltime = minutes*60 + seconds
        npics = int(totaltime/ntimeint)
        entries['Number of Pictures'].delete(0, END)
        entries['Number of Pictures'].insert(0, npics)
        print("# of Pictures: %f" % npics, " pictures")
    
def makeform(root, fields):
    entries = {}
    for field in fields:
        row = Frame(root)
        lab = Label(row, width=20, text=field, anchor='w')
        ent = Entry(row)
        ent.insert(0,"0")
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=NO, fill=X)
        entries[field] = ent
    return entries

def legality(entries):
    allowed = ".0123456789"
    timeint = entries['Time Interval (s)'].get()
    tottime = entries['Total Time (min.sec)'].get()
    pics = entries['Number of Pictures'].get()
    check1 = True
    for i in timeint:
        if i not in allowed:
            check1 = False
    check2 = True
    for i in tottime:
        if i not in allowed:
            check2 = False
    check3 = True
    for i in pics:
        if i not in allowed:
            check3 = False
    if check1 & check2 & check3:
        return True
    else:
        return False
##check 0 only entries
    

if __name__ == '__main__':
   root = Tk()
   root.title('Calculator')
   ents = makeform(root, fields)
   x = 5
   y = 5
   root.bind('bind', (lambda event, e=ents: fetch(e)))   
   btottime = Button(root, text='Total Time', command=(lambda e=ents: totaltime(e)))
   btottime.pack(side=LEFT, padx=x, pady=y)
   btimeint = Button(root, text='Time Interval', command=(lambda e=ents: timeint(e)))
   btimeint.pack(side=LEFT, padx=x, pady=y)
   bpics = Button(root, text='# Pictures', command=(lambda e=ents: totpics(e)))
   bpics.pack(side=LEFT, padx=x, pady=y)
   bquit = Button(root, text='Quit', command=root.quit)
   bquit.pack(side=LEFT, padx=x, pady=y)
   root.mainloop()

#https://www.youtube.com/watch?v=EwdKxDXAGBs
