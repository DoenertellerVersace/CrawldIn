import datetime
import time

from src.crawler import crawl

session_login = input("Bitte LinkedIn-E-Mail zur Anmeldung eingeben:\n")
session_passwd = input("Bitte LinkedIn-Passwort zur Anmeldung eingeben:\n")

tasks = []
failedTasks = []

output = {}

with open("../data/data_in.csv", "r") as file:
    count = 0
    for line in file:
        if count == 0:
            count += 1
            continue
        lineSplitted = line.split(";")
        tasks.append((lineSplitted[0],lineSplitted[1]))

print(f"Insgesamt {len(tasks)} Elemente zu bearbeiten...")

while len(tasks) != 0:
    temp = []
    if len(tasks) >= 3:
        for i in range(0, 3):
            temp.append(tasks.pop())
    else:
        for i in range(0, len(tasks)):
            temp.append(tasks.pop())
    tempOut, tempFailed = crawl(session_login,session_passwd,temp)
    output.update(tempOut)
    failedTasks += tempFailed
    time.sleep(5)
    print(f"\nNoch {len(tasks)} Elemente zu bearbeiten...")

print(f"Failed Tasks: {len(failedTasks)} Elemente.")



date = datetime.datetime.now()

with open(f'../data/failed_{date}.csv', "w") as file:
    file.write("ID;Name;;;\n")
    for k in failedTasks:
        file.write(k[0] + ';' + k[1] + ';;;\n')

print("\nDaten werden in Ausgabe-Datei geschrieben:\n")

with open(f'../data/data_out_{date}.csv', "w") as file:
    file.write("company,companySize,employeesOnLI,followersOnLI,link\n")
    for k in output:
        print(output[k]['name'] + "...")
        compData = [k]
        if "name" in output[k]:
            compData.append(output[k]["name"])
        else:
            compData.append("")
        if "compSize" in output[k]:
            compData.append(output[k]["compSize"])
        else:
            compData.append("")
        if "empOnLI" in output[k]:
            compData.append(output[k]["empOnLI"])
        else:
            compData.append("")
        if "followers" in output[k]:
            compData.append(output[k]["followers"])
        else:
            compData.append("")
        if "link" in output[k]:
            compData.append(output[k]["link"] + "\n")
        else:
            compData.append("\n")
        file.write(";".join(compData))
