import csv


def fix_csv(name: str):
    with open(name) as f_in, open('data/nyse.csv', 'w') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        next(reader)

        # Transform the rest of the lines
        for line in reader:
            if '^' not in line[0]:
                writer.writerow([line[0], line[1]])

    # with open(name, 'r') as file:
    #     reader = csv.reader(file)
    #
    #     # This skips the first row of the CSV file.
    #     next(reader)
    #
    #     for row in reader:
    #         if '^' not in row[1]:
    #             names.add(row[1])
    #
    # return names
