import datetime
import re

replacement = {'artificial intelligence':['artificial intelligence master','ai','m ai','master ai','msc artificial intelligence','msc artificial intelligence: cognitive science','uva ai'],
               'bioinformatics and systems biology':['bioinf','bioinformatics','bioinformatics & systems biology','bioinformatics and biology systems','bioinformatics and systems biology master\'s','bioinformatics and system biology','bioinformatics and systems biology msc','boinformatics','biosb','m bioinformatics','master of bioinformatics and system biology','msc bioinformatic','msc bioinformatics & systems biology','msc bioinformatics'],
               'computational science':['cls','clsjd','computational science joint degree','masters compuational science','msc computational science'],
               'computer science':['computer science (joint degree)','computer science masters','cs','cs (exchange)','master computer science','computer science - internet and web technologies', 'computer science big data engineering master','mscs','msc computer science (big data engineering)'],
               'business administration/business analytics':['mba','ba','business analytics and data science','business analytics','business administration','digital business & innovation','dbi digital business and innovation','master digital business and innovation', 'business administration: digital business & innovation','business adminitration','digital business and innovation'],
               'information sciences':['information studies: data science (uva)','ma data science (uva)','information studies','ds','uva: information systems - data science','uva msc information studies: data science','uva master information studies, track data science'],
               'finance':['quantitative risk management','qrm','msc qrm (dhp)','master of finance','dhpqrm','duisenberg qrm'],
               'humanities research':['rm humanities: linguistics','ma language technology'],
               'econometrics and operations research':['operation research','eor','econometrics and operations research','econometrics','financial econometrics','financial econometrivs','master econometrics','master econometrics & or','masters eor'],
               'health sciences':['master health sciences'],
               'management, policy analysis and entrepeneurship in health and life sciences':['master management, policy analysis and entrepeneurship in health and life sciences'],
               'other':['ms','x','multiple programmes'],
               'sociology':['exchange student (sociology)'],
               'stochastics and financial mathematics':['maths, stochastics, master, uva']}

months = [(lambda x:datetime.date(1900, x, 1).strftime('%B'))(x) for x in range(13)[1:]]+([(lambda x:datetime.date(1900, x, 1).strftime('%b'))(x) for x in range(13)[1:]])
months = [x.lower() for x in months]

def monthfinder(date):
    for month in months:
        x = date.find(month)
        if x != -1:
            return month, x
    return None, None

def numericalsplit(date):
    #only day or month or year
    if len(date) <= 2:
        
        #only year
        if int(date) > 31:
            date = "//19" + date
            
        #assuming only month
        elif int(date) < 13:
            date = "/" + date + "/"
                
        #only day, contains no information
        else:
            date = "//" 
        
    #only day/month, month/year or year
    elif len(date) == 4:
        
        #only year
        if (int(date[:2]) == 19) & (int(date[2:4])>12):    
            date = "//" + date
        
        else:
            #assuming year/month
            if int(date[:2]) > 31:
                date = "/" + date[2:] + "/" + "19" + date[:2]
            
            #assuming month/year
            elif int(date[2:]) > 31:
                date = "/" + date[:2] + "/" + "19" + date[2:]
            
            #assuming month/day
            elif int(date[2:]) > 12:
                date = date[2:] + "/" + date[:2] + "/"
            
            #assuming day/month
            else:
                date = date[:2] + "/" + date[2:] + "/"
    
    #only day/month/year or month/year
    elif len(date) == 6:
        
        #assuming year/month
        if int(date[:2]) == 19 & (int(date[2:4])>12):
            date = "/" + date[4:] + "/" + date[:4]
        
        #assuming month/year
        elif int(date[2:4]) == 19 & (int(date[4:])>12):
            date = "/" + date[:2] + "/" + date[2:]
        
        #assuming month/day/year
        elif int(date[2:4]) > 12:
            date = date[2:4] + "/" + date[:2] + "/19" + date[4:]
        
        #assuming day/month/year
        else:
            date = date[:2] + "/" + date[2:4] + "/19" + date[4:]
    
    #day/month/year
    elif len(date) == 8:
        
        if (int(date[:2]) == 19) & (int(date[2:4])>12):
            
            #assuming year/month/day
            if int(date[6:]) > 12:
                date = date[6:] + "/" + date[4:6] + "/" + date[:4]
            
            #assuming year/day/month
            else:
                date = date[4:6] + "/" + date[6:] + "/" + date[:4]

        else:
            
            #assuming month/day/year
            if int(date[2:4]) > 12:
                date = date[2:4] + "/" + date[:2] + "/" + date[4:]
            
            #assuming day/month/year
            else:
                date = date[:2] + "/" + date[2:4] + "/" + date[4:]
    
    return date

def fixdate(date):
    datelist = date.split('/')
    
    datelist = list(filter(None, datelist))
    if len(datelist) == 0:
        date = "//"
        
    elif len(datelist) == 1:
        date = numericalsplit(datelist[0])

    elif len(datelist) == 2:
        
        # year/month
        if int(datelist[0]) > 31:

            # check if full year
            if len(datelist[0]) == 2:
                datelist[0] = "19" + datelist[0]
            
            date = "/".join(["",datelist[1],datelist[0]])
        
        # month/year
        elif int(datelist[1]) > 31:
            
            # check if full year
            if len(datelist[1]) == 2:
                datelist[1] = "19" + datelist[1]
                
            date = "/".join(["",datelist[0],datelist[1]])
            
        # month/day
        elif int(datelist[1]) > 12:
            date = "/".join([datelist[1],datelist[0],""])
        
        # day/month
        else:
            date = "/".join([datelist[0],datelist[1],""])
    
    else:

        if int(datelist[0]) > 31:

            # check if full year
            if len(datelist[0]) == 2:
                datelist[0] = "19" + datelist[0]

            # year/month/day
            if int(datelist[2]) > 12:
                date = "/".join([datelist[2],datelist[1],datelist[0]])
                
            # year/day/month
            else:
                date = "/".join([datelist[1],datelist[2],datelist[0]])

        # assuming never */year/*

        else:

            # check if full year
            if len(datelist[2]) == 2:
                datelist[2] = "19" + datelist[2]

            # month/day/year
            if int(datelist[1]) > 12:
                date = "/".join([datelist[1],datelist[0],datelist[2]])
            
            # day/month/year
            else:
                date = "/".join([datelist[0],datelist[1],datelist[2]])

    return date

def removesep(date, sep):
    datelist = []
    for x in date:
        if x == sep:
            pass
        else:
            datelist.append(x)
    date = "".join(datelist)
    return date

def replacesep(date):
    datelist = []
    for x in date:
        if not (x.isalpha() or x.isdigit()):
            datelist.append("/")
        else:
            datelist.append(x)
    date = "".join(datelist)
    date = re.sub('/+', '/', date)
    date = fixdate(date)
    return date

def replacemonth(date):
    month, x = monthfinder(date)
    while month != None:
        index = months.index(month)%12+1
        date = date.replace(month," " + str(index) + " ")
        month, x = monthfinder(date)
    if month == None:
        pass
    date = re.sub(' +', ' ', date)
    date = date.strip()
    return date

def removealpha(date):
    datelist = []
    for x in date:
        if x.isalpha():
            pass
        else:
            datelist.append(x)
    date = "".join(datelist)
    date = re.sub(' +', ' ', date)
    return date

def splitbirthday(date):
    date = removesep(date, "\'")
    
    if bool(re.match('^(?=.*/.*)',date)):
        date = replacesep(date)
    
    if removesep(date," ").isalpha():
        month, x = monthfinder(date)
        if month == None:                                    #contains no information
            date = "//"
        else:
            date = replacemonth(date)
            date = removealpha(date).strip()
            if date.isdigit():
                date = numericalsplit(date)
        
    else:
        date = replacemonth(date)
        date = removealpha(date)
        if date.isdigit():
            date = numericalsplit(date)
        else:
            date = replacesep(date)
    date = date.split('/')
    return date

def removenonnum(number, integer = False):
    numlist = []
    comma = False
    for x in number:
        if not x.isdigit():
            if bool(re.match('^(?=.*,.*)',x)) or bool(re.match('^(?=.*\..*)',x)):
                if integer == False:
                    if comma == False:
                        numlist.append(".")
                        comma = True
                    else:
                        break
                else:
                    try:
                        y = int(number[number.index(x)+1])
                    except:
                        break
                    else:
                        if y < 5:
                            break
                        else:
                            numlist[-1] = str(int(numlist[-1])+1)
                            break
            else:
                pass
        else:
            numlist.append(x)
    number = "".join(numlist)
    number = re.sub(' +', ' ', number)
    return number

import string
def replacetimesep(time):
    times = []
    for x in time:
        if x.isdigit():
            times.append(x)
        elif x in string.punctuation and len(times) != 0:
            times.append(":")
        else:
            pass
    if len(times) > 5:
        times = times[:-2]
    if len(times) > 2:
        times.insert(-2, ":")
    if ":" not in times:
        times.append(":00")
    if times[0] == "24":
        times[0] = "00"
    return "".join(times)

def fixtime(time, period = None):
    time = removealpha(time).strip()
    time = replacetimesep(time)
    times = list(filter(None, time.split(":")))[:2]
    if period == "pm":
        times[0] = str(int(times[0])+12)
    elif period == None:
        if (12 >= int(times[0]) > 7):
            times[0] = str(int(times[0])+12)
    if len(times[-1]) < 2:
        times[-1] += "0"
    if len(times)== 1:
        return None 
    else:
        return ":".join(times)
