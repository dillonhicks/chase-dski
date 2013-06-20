
def main():
    contents = ""
    with open('syscalls.py', 'r') as scfile:
        contents = scfile.read()
        

    print "syscall_name_to_number = {"
    for line in contents.splitlines():
        try:
            name, number = line.split()
        
        except: 

            continue
        print "    {name:25} : {num}".format(name=repr(name), num=number)

    print
    print '}'

    print 

    print "syscall_number_to_name"
    for line in contents.splitlines():
        try:
            name, number = line.split()
        
        except: 

            continue
        print "    {num:5} : {name},".format(name=repr(name), num=number)

    print
    print '}'


#        print name, number


if __name__ == "__main__":
    main()
