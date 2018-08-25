

from ftplib import FTP
import re

'''
In case the url_list_imMcrobe_copypaste.txt bugs out, this exhaustive method to search the FTP server of iMicrobe
could be used to create the urls, maybe.  


Works!

Created list is named 'url_list_iMicrobe.txt'
'''

# Connect to FTP server iMicrobe
ftp = FTP("ftp.imicrobe.us")
ftp.login()

# get list of all samples to iterate and extract urls from
ftp.cwd("/projects/104/samples")
dd = ftp.nlst()

# init url list
urls = {}

# iterate directories to extract sample paths and if md5sum present

filen = "Data/url_list_iMicrobe.txt"
fd = open(filen, 'w')
# i = 0
for d in dd:
    l = ftp.nlst("/projects/104/samples/{d}".format(d=d))
    subl = [x for x in l if re.match(r'.*\.nt\.fa\.gz.*', x)]

    if len(subl) >= 1:
        paths = ["ftp://ftp.imicrobe.us" + x for x in subl]

        tit = re.findall(r'MMETSP....', subl[0])[0]
        fd.write(str(tit + '\t' + '\t'.join(paths) + '\n'))
        urls[tit] = paths
        print("DONE; ", tit)
    else:
        print('NO correct fasta file!!!!!!!!\n\n\n')
        print(l)
    # if i > 2: #debugg
    #     break
    # i += 1


ftp.quit()

fd.close()

