import requests
import json

url = "https://web.descript.com/v2/projects/00c80418-5066-4580-b4ad-988a0f93431d/published_projects"

payload = {}
headers = {
  'sec-ch-ua-platform': '"Windows"',
  'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjluTmxHQzlRbE5aOVU5TndhbG40cyJ9.eyJodHRwczovL2Rlc2NyaXB0LmNvbS9jdXJyZW50X2Nvbm5lY3Rpb25fbmFtZSI6IlVzZXJuYW1lLVBhc3N3b3JkLUF1dGhlbnRpY2F0aW9uIiwiaHR0cHM6Ly9kZXNjcmlwdC5jb20vaGFzX3Nzb19pZGVudGl0eSI6ZmFsc2UsImh0dHBzOi8vZGVzY3JpcHQuY29tL2hhc19nb29nbGVfaWRlbnRpdHkiOmZhbHNlLCJodHRwczovL2Rlc2NyaXB0LmNvbS9oYXNfZW1haWxfcGFzc3dvcmRfaWRlbnRpdHkiOnRydWUsImh0dHBzOi8vZGVzY3JpcHQuY29tL2VtYWlsX3Bhc3N3b3JkX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL2F1dGgwLmRlc2NyaXB0LmNvbS8iLCJzdWIiOiJhdXRoMHw2MTdhYTQ4MTc3NjViNjAwNzIxNTUyMmIiLCJhdWQiOlsiaHR0cHM6Ly9hcGkuZGVzY3JpcHQuY29tIiwiaHR0cHM6Ly9wcm9kLWRlc2NyaXB0LWF1dGguYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTc0NDI2MjA1MCwiZXhwIjoxNzQ0MjYzODUwLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIG9mZmxpbmVfYWNjZXNzIiwiYXpwIjoiVkRmdTdyZzRwZENFTFdzclFqY3cydEc2M2E4UWx5bWkiLCJwZXJtaXNzaW9ucyI6W119.KsOJD5Y8pctRaL9q7PG0D8t17kr3FvPHiJwb-q9VY850rzPLsseqKefoDQuUrpmTPnIyLAY7Ux4Wqb9Ze8YMJFjZq42WL6froqzGhaUTgLnWfVmiudGKfO5G4nVX6-UoeNhRp0hVF8NKPb2d0hX0n9NIe8J3xUvEEGBHcvaYoZAX079hL-qqnQ24_a7n2HtYc4pHs9fCHbUI-_UYsY__C6Rol6davEwu7823U5AbvIo3hbfDTa_Tj6WqdCeT-Nie784wOm4jEJhaCnIzkJOAp80xnQy6RmKrvDkV2Ya2dufJUSEdBkZhFbikuFBGSoYwGndkuf-QNPITzK0FgfSRiA',
  'x-descript-app-build-number': '20250409.25792',
  'x-descript-app-build-type': 'release',
  'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
  'sec-ch-ua-mobile': '?0',
  'x-descript-app-name': 'web',
  'traceparent': '00-5f2f9759cd100612060aa311364a8f11-00',
  'x-descript-auth': 'auth0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
  'Accept': 'application/json, text/plain, */*',
  'Accept-version': 'v1',
  'Content-Type': 'application/json',
  'x-descript-app-id': 'd4c17ff9-7f77-4dac-9d2f-97bb393871af',
  'x-descript-app-version': '112.0.1',
  'Sec-GPC': '1',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'host': 'web.descript.com',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)
response_json = json.loads(response.text)

for composition in response_json:
    print(composition['name'])
    # print(f"https://share.descript.com/view/{composition['url_slug']}")

