###
POST
http: // 127.0
.0
.1: 8000 / user / register /
Content - Type: application / json

{
    "email": "korotkovaad@icloud.com",
    "username": "nnk",
    "company": "nnk_company",
    "position": "economist",
    "password1": "hjvfrhenjq2003",
    "password2": "hjvfrhenjq2003"
}

###
POST
http: // 127.0
.0
.1: 8000 / partner / update /
Content - Type: application / json
Authorization: Token
f95b616aab96e094f61dd85d8a788988ea38fb48

{
    "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
}

###
POST
http: // 127.0
.0
.1: 8000 / user / login /
Content - Type: application / json

{
    "email": "korotkovaad@icloud.com",
    "password": "hjvfrhenjq2003"

}

###


GET
http: // 127.0
.0
.1: 8000 / user / details /
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

###

GET
http: // 127.0
.0
.1: 8000 / products / category /

###

GET
http: // 127.0
.0
.1: 8000 / shop /

###

GET
http: // 127.0
.0
.1: 8000 / products / info?shop_id = 1 & category_id = 224

###

GET
http: // 127.0
.0
.1: 8000 / basket /
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

###

POST
http: // 127.0
.0
.1: 8000 / basket /
Content - Type: application / json
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

{
    "items": "[{\"product_info_id\": 13, \"quantity\": 2}, {\"product_info_id\": 14, \"quantity\": 1}]"
}

###

DELETE
http: // 127.0
.0
.1: 8000 / basket /
Content - Type: application / json
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

{
    "items": "6,14"
}

###
GET
http: // 127.0
.0
.1: 8000 / shop / state /
Content - Type: application / json
Authorization: Token
f95b616aab96e094f61dd85d8a788988ea38fb48

###

POST
http: // 127.0
.0
.1: 8000 / shop / state /
Content - Type: application / json
Authorization: Token
f95b616aab96e094f61dd85d8a788988ea38fb48

{
    "state": "True"
}

###

GET
http: // 127.0
.0
.1: 8000 / user / contact /
Content - Type: application / json
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

###

POST
http: // 127.0
.0
.1: 8000 / user / contact /
Content - Type: application / json
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

{
    "city": "spb",
    "street": "kyst",
    "phone": "79138061716"
}

###


DELETE
http: // 127.0
.0
.1: 8000 / user / contact /
Content - Type: application / json
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

{
    "items": "1,2"
}

###

PUT
http: // 127.0
.0
.1: 8000 / user / contact /
Content - Type: application / json
Authorization: Token
99e4
ca22e216cfacacc56c4e303b7779fa8be07b

{
    "id": "3",
    "city": "spb1"
}