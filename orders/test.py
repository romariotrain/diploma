import requests
import yaml


response = requests.get('https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml')
# response.encoding = 'cp 1252'
data = yaml.safe_load(response.content)

print(data)