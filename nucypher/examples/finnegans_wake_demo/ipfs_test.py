import ipfsapi
api = ipfsapi.connect('127.0.0.1', 5001)
res = api.add('pasport.jpg')
print (res)
#print (api.cat(res['Hash']))
