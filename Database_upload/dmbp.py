import urllib.request


url = "ftp://ftp.imicrobe.us/projects/104/samples/2054/MMETSP0527.nt.fa.gz.md5"

req = urllib.request.Request(url)
response = urllib.request.urlopen(req)
the_page = response.read()
p = the_page.split()[0]
md = str(p).split("\'")

print(md[1])