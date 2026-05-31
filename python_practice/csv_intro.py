import csv

# with open(r'E:\APC_Analysis_4.0\Win64\Color_PDFX4\ERROR_REPORT.CSV','r') as csv_file:

#     #give me list where each row is a new list and each column is a new entry of list
#     csv_content= csv.reader(csv_file)

    # to skip first line ie header 
    # next(csv_content)
    # for line in csv_content:
    #     print(line[1])

    #Now how to write in csv

    # with open(r'E:\APC_Analysis_4.0\Win64\Color_PDFX4\ERROR_REPORT_copied.CSV','w') as copied_csv:

    #     csv_writer=csv.writer(copied_csv,delimiter='\t')

    #     for line in csv_content:
    #         csv_writer.writerow(line)


#now reading this Tab separated file without using and delimiter

# with open(r'E:\APC_Analysis_4.0\Win64\Color_PDFX4\ERROR_REPORT_copied.CSV','r') as copied_csv:
#     #When delimiter wwas not used data was printed like this:
#     # ['AutomatedTest-joboptions-bugsFullRun\tColr_Pdfx4_66.ps\t\t undefined; OffendingCommand: setdistillerparams; ErrorInfo: CalCMYKProfile Coated FOGRA27 (ISO 12647-2:2004) ]%%\tmissing\tmissing\tissue\tok\tReran again by placing the Color profile used at the path - C:\\Windows\\System32\\spool\\drivers\\color .The file ran successfully and was PDFX/4 Complaint.']
#     # You can see it is not seprated as default deliminter is "," 
#     csv_reader= csv.reader(copied_csv,delimiter='\t')

#     for line in csv_reader:
#         print(line)


#now these were methods to read and write in csv but the Preferred methods are DictReader and DictWriter

with open(r'E:\APC_Analysis_4.0\Win64\Color_PDFX4\ERROR_REPORT.CSV','r') as csv_file:

    csv_reader=csv.DictReader(csv_file)

    #using this each row is now a dictionary and also header line is removed automatically
    # as they are now keys for each item in dictionary
    # for line in csv_reader:
    #     print(line)

    with open(r'E:\APC_Analysis_4.0\Win64\Color_PDFX4\ERROR_REPORT_dictWriter.CSV','w') as new_csv:

    
        #we need to specify fieldnames in order to write in CSV using DictWriter
        #fieldnames= ['JobOption','TestName','ErrorExpected','ErrorReported','fyi:BasePDFStatus','fyi:TestPDFStatus','issue or not?','']

        #csv_writer= csv.DictWriter(new_csv,fieldnames=fieldnames,delimiter='\t')

        # for line in csv_reader:
        #     csv_writer.writerow(line)

        #Now suppose i dont want some column in my csv with normal method i need to do indexing then 
        # here see how

        fieldnames = ['TestName','ErrorExpected','ErrorReported','issue or not?']
        csv_writer= csv.DictWriter(new_csv,fieldnames=fieldnames)

        
        for line in csv_reader:
            
            line.pop('JobOption')
            line.pop('fyi:BasePDFStatus')
            line.pop('fyi:TestPDFStatus')
            line.pop('')
    
            #print(line)
            csv_writer.writerow(line)






         

    