def main(inputfile, columns):
    """ Changes the seperator from space to tab in a text file. """
    file = open(inputfile, 'r')
    lines = file.readlines()
    for line in lines:
        parts = line.split(sep=' ')
        if columns == 2:
            newline = parts[0] + '\t' + parts[1] + '\n'
        else:
            newline = parts[0] + '\t' + parts[1] + '\t' + parts[2] + '\t' + parts[3] + '\n'
        with open(inputfile + 'spacetotabs' +'.txt', 'a') as the_file:
            the_file.write(newline)

    inputfilename = inputfile + 'spacetotabs'
    inputfile2 = inputfilename +'.txt'
    # write a new file without empty lines
    for line in open(inputfile2):
        if len(line) > 1 or line != '\n':
            with open(inputfilename + "no_whiterules.txt", 'a') as file:
                file.write(line)

