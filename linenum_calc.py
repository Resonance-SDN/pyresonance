# Author: Arpit Gupta (glex.qsd@gmail.com)
# Simple program to list all the file in a directory and calculate the line numbers
# Line number calculation will avoid 'empty lines' and 'comments'
#

import os,sys
ofile = open('lines.txt','w+')

def getlines(dirs):
    n = 0
    ln=0
    ifile = open(dirs,'r')
    flag = 0
    for line in ifile.readlines():
        ln+=1
        if flag== 0:
            line = line.strip(' ')
            if line.startswith('#') or line =='\n' or line.startswith('"""'):
                if line.startswith('"""'):
                    if line.count('"""')!=2:
                        flag=1
                        #continue
            else:
                n+=1
        else:
            if '"""' in line:
                flag=0

    return n

fdir_prev=''
for r,d,f in os.walk(os.getcwd()):
    for files in f:
        if files.endswith('.py'):
            print files
            dirs = os.path.join(r,files)
            fdir = dirs.split(files)[0]
            if fdir!=fdir_prev:
                ofile.write('\n\n## Dir: '+fdir+'\n')

            n_line = getlines(dirs)
            ofile.write(files+': '+str(n_line)+'\n')


            fdir_prev= fdir
