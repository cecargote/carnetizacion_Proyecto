print ("archivo de prueba")

import requests
import json
ci = "97041207064"
area = "DG de ICI Area Central"


reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/areas"

headersList = {
 "Accept": "*/*",
 "User-Agent": "Thunder Client (https://www.thunderclient.com)",
 "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=" 
}

payload = ""

response = requests.request("GET", reqUrl, data=payload,  headers=headersList)

result = json.loads(str(response.text))
       
lista=""
count =0
for iter in result:
    count= count +1
    if iter['name'] == area:
        
        area = iter['distinguishedName']
        break

print(count)
print (area)





reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/search-all"

headersList = {
 "Accept": "*/*",
 "User-Agent": "Thunder Client (https://www.thunderclient.com)",
 "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=",
 "Content-Type": "application/json" 
}

payload = json.dumps({
    "identification": ci,
    "name": "",
    "lastname": "",
    "surname": "",
    "email": "",
    "area": area
})

response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
result = json.loads(str(response.text))
prueba = None
print(result[0]['name'])
if prueba is not None:
    print("es none")
print(bool(result))
