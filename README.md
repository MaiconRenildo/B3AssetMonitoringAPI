# B3 Asset Monitoring API
API de monitoramento de ativos da B3

## Requisitos
- [VS code](https://code.visualstudio.com/download)
- [VS code remote containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Clone do projeto

```
  git clone git@github.com:MaiconRenildo/B3AssetMonitoringAPI.git
  cd B3AssetMonitoringAPI
```

  > <strong>Observações importantes</strong>: <ul><li>Antes de qualquer coisa é necessário preencher o arquivo <em>.env</em>  seguindo o padrão documentado no arquivo <em>.env.example</em>. Uma API key válida para a variável HG_API_KEY pode ser obtida no site da [HG brasil](https://hgbrasil.com/) </li><li>Para ter acesso ao ambiente de desenvolvimento configurado utilize o devcontainer por meio da [VS code remote containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)</li><li>Se STAGE for igual a 'TEST', então o banco sqlite será utilizado. Caso contrário será utilizado o mysql</li><li>Por padrão o servidor vai ser executado na porta 8000</li> </ul>


## Execução dos testes
Para executar os testes, certifique-se que a variável STAGE no arquivo .env está com o valor 'TEST' e execute o comando no terminal
```
pytest
```
Feito isso, o resultado será como o da imagem a seguir <br>
![tests-b3](https://user-images.githubusercontent.com/63758491/185661216-cd8be392-6b40-4376-adcc-e19ea3b09e12.png)

## Execução do projeto
Há duas possibilidades de execução do projeto: <ul><li>Acessar o terminal do container de desenvolvimento e executar o comando ```rq worker monitoring email --with-scheduler``` em paralelo com o ```uvicorn api.main:app --host 0.0.0.0 --port 8000``` </li><li>Utilizar o comando ```docker-compose up```</li></ul>


# Rotas
## GET / 
Rota da documentação da api. Exibe a página a seguir
![docs-b3](https://user-images.githubusercontent.com/63758491/185722319-b0bd155f-bba2-40e5-b800-765d6fdc8099.png)

## User


## POST /user
Rota de criação de usuário
#### Parâmetros
<ul><li>name</li><li>email</li><li>password</li></ul>

Exemplo:
```
{
    "email":"anny@gmail.com",
    "name":"Anny",
    "password":"password"
}
```

#### Respostas
##### Created 201
```
{
  "message": "User created successfully"
}
```

##### Not Acceptable 406
```
{
  "detail": "Email not available"
}
```
##### Unprocessable Entity 422
```
{
  "detail": "Invalid email"
}
```









## POST /user/login
Rota de login
#### Parâmetros
<ul><li>email</li><li>password</li></ul>

Exemplo:
```
{
    "email":"anny@gmail.com",
    "password":"password"
}
```

#### Respostas
##### OK 200
```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
}
```

##### Unauthorized 401
```
{
  "detail": "Invalid email or password"
}
```


## B3
Rotas relacionadas aos ativos da B3. Para utilizá-las é necessário efetuar o processo de login e passar o token recebido no Authorization da requisição

Retorno caso seja passado um token inválido:
#####  Unauthorized 401
```
{
  'detail': 'Invalid token'
}
```
Retorno caso o token não seja informado:
#####  Forbidden 403
```
{
  'detail': 'Not authenticated'
}
```




## GET /b3/assets
Rota de listagem dos ativos da B3
#### Parâmetros
<ul><li>page</li><li>limit</li></ul>

#### Respostas
##### OK 200
```
[
  {
    "company_name": "COSAN",
    "code": "CSAN3",
    "CNPJ": "50746577000115"
  },
  {
    "company_name":"MAGAZ LUIZA"
    "code":"MGLU3",
    "CNPJ":"47960950000121"
  }
]
```
  
  
  
  
## GET /b3/assets/cotation
Rota de busca da cotação de um ativo da B3.
#### Parâmetros
<ul><li>asset_code</li></ul>

#### Respostas
##### OK 200
```
{
  "code": "CSAN3",
  "cotation": "4.1"
}
```
##### Not found 404
```
{
  "detail": "Code not found"
}
```
  

  
## POST /b3/assets/monitoring
Rota responsável por habilitar o monitoramento de um ativo. Através dela é possível definir um plano de investimento. Isto é, definir um ponto de entrada(lower_price_limit) e um ponto de saída(upper_price_limit). A partir do momento em que a requisição é feita, a cotação da ação será monitorada a cada minuto(isso se o mercado estiver aberto). Se a cotação atingir ou ultrapassar o valor de entrada, um e-mail de recomendação de compra será enviado. Da mesma forma, se a cotação atingir o valor de saída, um e-mail será enviado recomendando a venda. Note que ambas as recomendações podem ser enviadas no máximo uma vez, a não ser que os parâmetros de monitoramento sejam atualizados.
  
  
#### Parâmetros
<ul><li>asset_code</li><li>upper_price_limit</li><li>lower_price_limit</li></ul>

  
Exemplo:
```
{
  "asset_code": "CSAN3",
  "upper_price_limit": 45.4,
  "lower_price_limit": 10.5
}
``` 
  
  
#### Respostas
##### OK 200
```
{
  "message": "Now the asset is being monitored"
}
```
##### Not found 404
```
{
  "detail": "Code not found"
}
```
##### Not acceptable 406
```
{
  "detail": "Asset already monitored"
}
```
##### Unprocessable Entity 422
```
{
  "detail": "Invalid limits"
}
```
  
  
  
  
  
  
  
  
  
## PUT /b3/assets/monitoring
Rota responsável por atualizar os parâmetros de monitoramento de um ativo. Ao atualizar os parâmetros o histórico de recomendações é zerado. 
  
#### Parâmetros
<ul><li>asset_code</li><li>upper_price_limit</li><li>lower_price_limit</li></ul>

  
Exemplo:
```
{
  "asset_code": "CSAN3",
  "upper_price_limit": 45.4,
  "lower_price_limit": 10.5
}
``` 
 
#### Respostas
##### OK 200
```
{
  "message": "Asset monitoring params updated"
}
```
##### Not found 404
```
{
  "detail": "Code not found"
}
```
##### Unprocessable Entity 422
```
{
  "detail": "Invalid limits"
}
```

## DELETE /b3/assets/monitoring
Rota responsável por desabilitar o monitoramento de um ativo.
  
#### Parâmetros
<ul><li>asset_code</li></ul>

  
Exemplo:
```
{
  "asset_code": "CSAN3",
}
``` 
 
#### Respostas
##### OK 200
```
{
  "detail": "Now the asset is not more being monitored"
}
```
##### Not found 404
```
{
  "detail": "Asset monitoring not found"
}
```

  
## GET /b3/assets/monitoring
Rota responsável por buscar os parâmetros de monitoramento criados pelo usuário. Caso um asset_code seja passado como parâmetro, somente os dados referentes a ele serão retornados. Caso contrário, serão retornados todos os existentes.
  
#### Parâmetros
<ul><li>asset_code    #opcional</li></ul>
 
#### Respostas
##### OK 200
```
[
  {
    "code": "CSAN3",
    "upper_price_limit": 45.4,
    "lower_price_limit": 10.5
  }
]
```
##### Not found 404
```
{
  "message": "Asset monitoring not found"
}
```
