import csv
import os
def write2onefile():
    files = [
        "training1.csv","training2.csv",
        "training3.csv","training4.csv",
        "training5.csv","training6.csv",
        "training7.csv","training8.csv",
        "training9.csv","training10.csv",
        "training11.csv","training12.csv",
        "training13.csv","training14.csv",
        "training15.csv","training16.csv"
    ]
    with open("outfile","w",encoding="utf-8", newline='') as fw:
        writer = csv.writer(fw)
        
        for file in os.listdir("."):
            if file.endswith("-post.csv"):    
                with open(file, encoding="utf-8") as csvfile:
                    info = csv.reader(csvfile, delimiter=',')
                    info_types = []
                    comment = 0
                    for row in info:
                        
                        writer.writerow(row)
    return
write2onefile()