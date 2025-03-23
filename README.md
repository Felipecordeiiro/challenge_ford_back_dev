## Quick Setup
Para essa solução usamos o gerenciador de pacotes uv, então antes de mais nada, é interessante que você tenha instalado esse gerenciador (a escolha do mesmo é baseado na sua performance superando opções comuns, como: conda ou poetry), para isso você deve rodar o seguinte comando:

```
pip install uv
```

Em seguida você pode estar criando um novo ambiente na raiz desse diretório usando o comando:

```
uv venv --python 3.11
```

E, por fim, configurando todo o projeto a partir de um único comando:

```
uv sync
```

O diferencial do FastAPI é que disponibiliza, além do muito rápido, também uma documentação da API (swagger). Como essa solução também foi feita usando Docker para que você consiga entender como cada rotas da API funciona, seus argumentos e retornos você só precisa rodar o servidor através do comando:

```
docker compose up --build
```

Para buildar toda a imagem docker, que já subirá com um postgresql. E acessar através do seu browser:

```
http://localhost:8000/docs
```

Para análise dos testes integrados, aconselha-se que você rode após testagem das rotas da API. Para isso, basta que você entre no ambiente virtual que foi criado através do seguinte comando:

No windows:
```
#bash
source .venv/Scripts/activate

#powershell
.venv/Scripts/activate
```

No ubuntu:
```
source .venv/bin/activate
```

Dentre todas as 5 etapas obrigatórias do desafio, eu consegui realizar todas as básicas:
*   [ x ] Modelagem do banco de dados e uso do ORM: até 1 ponto.
*   [ x ] Implementação da API REST e das rotas de analytics: até 3 pontos.
*   [ x ] Implementação do sistema de autenticação e autorização: até 1 pontos.
*   [ x ] Segurança da aplicação e criptografia de dados sensíveis: até 2 ponots.
*   [ x ] Qualidade e cobertura dos testes automatizados: até 1 ponto.
*   [ x ] Organização do código, legibilidade e documentação: até 2 ponto.

Além dessas, consegui também realizar essas diferenciais, com um adendo para o Docker & CI/CD, pois não consegui automatizar os testes via github actions, para tanto. 

*   Implementação dos diferenciais :
    - [ ] cache: +1 ponto
    - [ x ] Docker & CI/CD: +1 pontos
    - [ x ] CORS: +1 ponto