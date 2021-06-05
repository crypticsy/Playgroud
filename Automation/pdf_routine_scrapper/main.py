import os, PyPDF2 


# creating a pdf file object 
path = os.path.dirname(os.path.abspath(__file__))
pdfFileObj = open(path+'/data.pdf', 'rb') 
  
# creating a pdf reader object 
pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
  

mygroup = "C2"      # Enter the group name to find the routine for a particular group
page_count = pdfReader.numPages
week = {"SUN":"Sunday","MON":"Monday","TUE":"Tuesday","WED":"Wednesday","THU":"Thursday","FRI":"Friday" }
database = {}

for page in range(page_count):
    pageObj = pdfReader.getPage(page)
    all_lines = list(pageObj.extractText().split('\n'))

    while all_lines!=[]:        # data extraction
        cur = all_lines.pop(0)
        if cur.upper() in week:
            database.setdefault(cur,[])
            data = [all_lines.pop(0) for _ in range(8)]
            if mygroup.upper() in data[5].upper():
                database[cur].append(data)


with open(path+"/routine.txt", "w") as file:
    for day in week:
        data = database[day]
        data.sort(key = lambda x: (x[0][6:8],x[0]))
        output = "------------------- %s -------------------\n"%(week[day])
        for i in data:
            temp = [i[0], i[2], i[3], "[ "+ i[4]+ " ]", "-->" , i[5], "( "+i[1]+" )",":",i[7]]
            output += '   '.join(temp) + "\n"
        output += "\n"
        # print(output)         # View the output while debugging
        file.write(output)

# closing the pdf file object 
pdfFileObj.close() 