import google.generativeai as genai
genai.configure(api_key="AIzaSyDAoECy7gh6itnEFBZKpfTdrZBRql4SReA")
for m in genai.list_models():
    print(m.name)
