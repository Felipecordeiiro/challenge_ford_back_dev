## Case para Teste Técnico de Desenvolvedor Back-end Python (Nível Entry Level)

**Objetivo:** Criar uma API REST para Gestão de Clientes, Transações e Analytics.

**Contexto:**

Você foi contratado para desenvolver uma API REST que permitirá o gerenciamento de suppliers, transações e a geração de alguns dados analíticos básicos. Essa API será utilizada por um sistema de CRM interno para auxiliar na gestão de suppliers e na análise de dados de vendas e garantias.

**Requisitos:**

1.  **Modelagem do Banco de Dados:**
    *   Defina as tabelas necessárias para armazenar informações sobre suppliers, transações (compras e emissão de garantia) e quaisquer outras tabelas que julgar relevantes para o contexto.
    *   Considere os sql e diagrama disponivel em anexo
    *   Escolha um ORM de sua preferência (ex: SQLAlchemy, SQLModel) para interagir com o banco de dados.
    *   Implemente as migrações do banco de dados para criar e atualizar as tabelas.
    *   Crie scripts para popular (semear) as tabelas com dados de exemplo para facilitar os testes.

2.  **API REST:**
    *   Crie endpoints para realizar as operações CRUD (Create, Read, Update, Delete) nas tabelas, foque em bulk load e retrival, pense q mts dados serão requisitados de uma vez.
    *   Implemente rotas para consultas específicas e filtros (ex: listar suppliers por nome, listar transações por tipo e período).
    *   Crie endpoints para gerar dados analíticos, exemplos abaixo, sinta-se livre:
        *   Total de vendas por supplier / parte.
        *   Número de garantias emitidas por supplier / modelo.
        *   Valor médio das transações por tipo (compra/garantia) ou por modelo.

3.  **Autenticação e Autorização:**
    *   Implemente um sistema de autenticação utilizando JWT (JSON Web Tokens) ou OAuth 2.0.
    *   Crie rotas para registro de novos usuários, login (gerar sessão) e logout (eliminar sessão).
    *   Proteja as rotas da API que exigem autenticação.

4.  **Segurança:**
    *   Criptografe dados sensíveis, como o CPF dos suppliers, utilizando uma biblioteca de criptografia (ex: cryptography, bcrypt).
    *   Explique a estratégia de segurança utilizada para proteger os dados e a API.

5.  **Testes Automatizados:**
    *   Crie testes automatizados para verificar o funcionamento das rotas de autenticação e das rotas de analytics.
    *   Não é necessário criar testes para todas as rotas CRUD, mas demonstre a capacidade de escrever testes unitários e de integração.
    *   Como os dados são ficticios e poucos, não precisa escrever testes de degradação, não serão avaliados.

**Diferenciais (Opcional):**

Cada um desses items vai te render mais pontos, então serve de quesito de desempate.

1.  **Cache:**
    *   Implemente uma estratégia de cache server-side para armazenar dados frequentemente acessados e sessões de usuário.
    *   Utilize um sistema de cache como Redis ou Memcached para melhorar o desempenho da API.

2.  **Docker e CI/CD:**
    *   Crie um Dockerfile para containerizar a aplicação.
    *   Publique o código no GitHub.
    *   Configure uma pipeline de CI/CD utilizando o GitHub Actions para automatizar os testes e o deploy da aplicação.

3.  **CORS:**
    *   Configure o CORS (Cross-Origin Resource Sharing) para permitir que a API seja acessada por diferentes domínios.

**Observações:**
*   Você deve utilizar o framework Python FastAPI.
*   Priorize a organização do código, a legibilidade e a qualidade da solução.
*   Documente o código de forma clara e concisa.
*   Justifique as escolhas de design e as decisões tomadas durante o desenvolvimento.

**Entrega:**

Os 4 pontos abaixo são obrigatorios, pois são oq vamos usar para avaliar seu teste.

*   Código fonte da API (URL do Repositorio no GitHub).
*   Documentação da API (ex: utilizando Swagger/OpenAPI).
*   Instruções para executar a aplicação (README).
*   Explicação da estratégia de segurança utilizada (Sessão no README).

**Critérios de Avaliação:**

*   [ ] Modelagem do banco de dados e uso do ORM: até 1 ponto.
*   [ ] Implementação da API REST e das rotas de analytics: até 3 pontos.
*   [ ] Implementação do sistema de autenticação e autorização: até 1 pontos.
*   [ ] Segurança da aplicação e criptografia de dados sensíveis: até 2 ponots.
*   [ ] Qualidade e cobertura dos testes automatizados: até 1 ponto.
*   [ ] Organização do código, legibilidade e documentação: até 2 ponto.
*   Implementação dos diferenciais :
    - [ ] cache: +1 ponto
    - [ ] Docker & CI/CD: +1 pontos
    - [ ] CORS: +1 ponto

Este case tem como objetivo avaliar suas habilidades técnicas em desenvolvimento back-end com Python, sua capacidade de resolver problemas e sua familiaridade com as melhores práticas de desenvolvimento de APIs REST. Boa sorte!
