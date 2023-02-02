print ("archivo de prueba")

import pandas

archivo = 'C:/Users/Carlos Laptop/Downloads/datos2.xlsx'
  

hoja = pandas.read_excel(archivo,engine="openpyxl")


#print(hoja["ci"])
list = hoja

#print(list["ci"])

result = list[(list["name"]=="juan")]

print(result)
print("no se encontro")
i=0
size = len(list)
while i< size:
   last_name_temp= list.iloc[i,3]
   name_temp= list.iloc[i,2]
   ci_temp = list.iloc[i,1]
   ci_temp = ""+str(ci_temp)
   
   if(name_temp=="Andrés" and last_name_temp =="Carvajal Elena" or ci_temp=="98012108648" ):
      cargo_temp= list.iloc[i,6]
      print(i, " ",ci_temp," " ,name_temp," ",last_name_temp," cargo: ",cargo_temp)
   i+=1

cargo = result["ocupation"]

string = str(cargo.values)
print(string)
newstring = ""+ string.replace("['","")
newstring = ""+ newstring.replace("']","")
print(newstring)

print("holaaa")
#for iter in list:
 #   print(iter)
  #  if str(iter) == "87122009159":
     #   print ("found")
     #   print("index: ", list.i)
        #print(list.iloc[list.index])
        

import requests
import json

import requests
import json

reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/student/fileStudent/getStudentAllData/97041207064"

headersList = {
 "Accept": "*/*",
 "User-Agent": "Thunder Client (https://www.thunderclient.com)",
 "Authorization": "Basic ZGlzZXJ0aWMud3Muc2lnZW51OmRpc2VydGljLndzKjIwMTUq",
 "Content-Type": "application/json" 
}

payload = json.dumps("")

response = requests.request("GET", reqUrl, data=payload,  headers=headersList)

#print(response.text)

result = json.loads(response.text)
tipo =result[0]["docentData"]['studentStatus']
print(tipo)