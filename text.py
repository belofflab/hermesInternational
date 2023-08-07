import requests




res = requests.get("https://www.fishisfast.com/ru/stores").text 



with open("test.html", "w", encoding="utf-8") as f:
    f.write(res)