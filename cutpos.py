import random

file = open("positive.txt", "r", encoding="utf-8")
outfile = open("postest1.txt", "w", encoding="utf-8")
for line in file:
    rand = random.randint(0,1)
    if rand:
        outfile.write(line)

file.close()
outfile.close