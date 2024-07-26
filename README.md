# Iniciação Científica

Este projeto foi utilizado para a Iniciação Científica da Universidade Federal de Uberlândia - Câmpus Monte Carmelo com o tema: Geração Automática de Relatórios de Confiabilidade: Projeto e implementação de análise de grupos de falhas de software e identificação de suas causas na Plataforma X-RAT.

### Objetivo

O principal objetivo deste estudo é responder as seguintes perguntas de pesquisa:  

- (1) Quais são as causas mais prevalentes das falhas de software analisadas? 
- (2) Onde elas se manifestam com maior frequência? 
- (3) Quais são os tipos mais comuns de causas de falhas? 

Além de analisar as causas das falhas de software, também serão investigados grupos de computadores, com especial atenção na identificação de padrões de falhas. Pelo menos três grupos de computadores serão analisados, abrangendo laboratórios de ensino, ambientes empresariais e ambientes de uso pessoal. Esta análise de grupos de computadores visa responder outras perguntas de pesquisa, tais como:  

- (1) Em quais grupos ocorrem mais falhas de software? 
- (2) Existem padrões de falhas específicos de determinados grupos de computadores? 
- (3) Quais fatores ambientais influenciam a ocorrência de determinadas falhas? Todas as análises devem ser automatizadas e integradas à plataforma X-RAT. Ao final, um relatório abrangente deve ser gerado, cobrindo tanto a confiabilidade de computadores individuais quanto de grupos de computadores.

### Estrutura do Projeto

![Estrutura do Projeto](/assets/image.png)

### Tecnologias utilizadas

- `Angular`
- Python
- FastAPI
- PostgreSQL

### Como Executar o Projeto

1. Clone o repositório para sua máquina local:

   ```bash
   git clone https://github.com/nathanmota-dev/scientific-research
   ```

2. Navegue até o diretório do projeto:

   ```bash
   cd scientific-research
   cd client
   ```

3. Instale as dependências:

   ```bash
   npm install
   ```

4. Inicie o servidor de desenvolvimento:

   ```bash
   npm start
   ```

5. Abra seu navegador em: [http://localhost:3000/](http://localhost:3000/) para visualizar o projeto em execução.

6. Navegue até o diretório do projeto

    ```bash   
   cd server
   ```

7. Instale as dependências:

   ```bash
   venv\Scripts\activate
    pip install -r requirements.txt
   ```

8. Inicie o servidor de desenvolvimento:

   ```bash
   uvicorn app.main:app --reload
   ```

9. Abra seu navegador em: [http://127.0.0.1:8000](http://127.0.0.1:8000) para visualizar o projeto em execução.

### Colaboradores

- [Nathan Mota](https://github.com/nathanmota-dev)
- [Alvaro Rodrigues](https://github.com/alvarojpr)