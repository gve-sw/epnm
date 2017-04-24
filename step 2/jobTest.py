import requests

url = "https://198.18.134.7/webacs/api/v1/op/jobService/runhistory.json"

querystring = {"jobName":"JobCliTemplateDeployIOSDevices09_56_50_574_PM_04_21_2017"}

headers = {
    'authorization': "Basic dXNlcjpUZXN0ZXIxMjM=",
    'cache-control': "no-cache",
    'postman-token': "6b9fdfb0-1fa7-7698-0e16-3dab07dd3004"
    }

response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

print(response.text)