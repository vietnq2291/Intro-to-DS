import csv

filename = 'googleHotelLondon.csv'
data = []

# open CSV-file
with open(filename, 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data.append(row)

# splite whole text in stars and review
stars = []
text = []
for row in data:
    tmp = row[1].split('/5', 1)
    if len(tmp) > 1:
        stars.append(tmp[0][-1])
        text.append(tmp[1])

# override data with splitted review and stars
for rowIdx in range(len(data)):
    data[rowIdx][1] = text[rowIdx]
    data[rowIdx].append(stars[rowIdx])

# create new file
cleanedFile = 'cleaned_file.csv'
with open(cleanedFile, 'w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerows(data)
