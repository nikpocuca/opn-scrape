import csv
import pdb



name = []
niknames = []

with open('names.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
	print(row)
	#pdb.set_trace()
        #dates.append(row[0])
        #scores.append(row[1])
	name.append(row[0])
	nikname = row[1:-1]
	nikname.append(row[-1])
	niknames.append(nikname)


name_dict = {}

count = 0
for nm in name:
	name_dict[nm] = niknames[count]
	count = count + 1 

print(name)
print(niknames)




