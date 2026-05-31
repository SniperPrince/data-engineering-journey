#file Objects
#To open file in read mode and if we dont specify anthing by default read.'w' for write,'a'for append,'r+'for read and write
# file = open('E:\\4159612_Logs.txt','r')

# print(file.name)
# print(file.mode)

# file.close()

#We will use context manager as wwe dont need to close file it automatically closes once we come out of block
#but still we have acces to variable f we usex to open outisde block but we cant read the file now but f.closed() will give true

#with open('E:\\4159612_Logs.txt','r') as f:
    
    #This method loads all lines at once can cause memory issue in case of large files
    # file_contents=f.read()
    #print(file_contents)

    
    #file_contents=f.readlines() # will give list of lines in file 
    #file_contents=f.readline() #will gve first line only but if run again then will give second then third like this
    
    #This below is also good to print lines one by one
    # for line in f:
    #     print(line,end='')
    
    #file_contents=f.read(100) # this will read first 100 characters and if we use again then read next 100
    #but once it reaches end of file it gives back empty string

    #Demo here:

    # size_to_read=10
    # file_contents=f.read(size_to_read)

    # print(file_contents)
    # f.seek(0) # this will bring back put pointer to start , or we can specify postion we want to bring it 
    # file_contents=f.read(size_to_read)
    # print(file_contents)
    
    #this will keep on reading 10 characters ut once it reaches EOF it give empty sting and then condtion becomes false
    # while len(file_contents)>0:
    #     print(file_contents,end='*')
    #     file_contents=f.read(size_to_read)




    #print(file_contents)

    # with open('test.txt', 'w') as f:
    #     f.write('Test')
    #     #if we again use write then it will wirte at the next postion

    #     #f.write('Test')
    #     #seek() brings pointer to 0th position and then when i write it overwrites the content
    #     f.seek(0)
    #     f.write('R')

    # with open('E:\\4159612_Logs.txt','r') as rf:
    #     with open('Copied.txt','w') as wf:
    #         wf.write(rf.read())

    #Now to copy images we need to use binary mode ie to read open it in 'rb' and tonwrite open it in 'wb'

    # with open(r"C:\Users\chansharma\Desktop\Pic.jpg",'rb') as rf:
    #     with open('Copied_image.jpg','wb') as wf:
    #         chunk_size=4096
    #         read_chunk=rf.read(chunk_size)

    #         while len(read_chunk) > 0:
    #             wf.write(read_chunk)
    #             read_chunk=rf.read(chunk_size)

