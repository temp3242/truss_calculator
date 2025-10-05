# Truss Calculator
Calculadora de forças de treliças usando a biblioteca anaStruct(https://github.com/ritchie46/anaStruct).

## Descrição
Este código calcula as forças de reação em apoios não livres e as forças internas de cada elemento (Componentes x,y e o módulo orientado (<b>" + "</b> => Tração, <b>" - "</b> => Compressão))

## Setup

 - ### Crie o ambiente virtual
        python3 -m venv .venv
 - ### Instale as dependencias
        .venv/bin/pip3 install -r requirements.txt

## Rodando o programa
    .venv/bin/python src/main.py

## Formato do arquivo de especificações
    "Nome do nó"; Coordenada x; Coordenada y;
    (Repete para todos os nós)
    Matriz de adjacência (0 = sem ligação, 1 = ligação);
    (Repete para todas as linhas da matriz, onde cada linha é um nó)
    Componente X da Força aplicada no nó; Componente Y da Força aplicada no nó; (Ambos em N)
    (Repete para todos os nós)
    Tipo de apoio do nó (P = Pino, N = Livre, X = Engaste, Y = Rolamento);
    (Repete para todos os nós)
    Módulo de elasticidade do material dos elementos (em Pa); Diâmetro dos elementos (em m);

## Membros
- ### Arthur Gaudêncio Odebrecht Stern
- ### Gabriel Araújo da Silva Domingos Ferreira
- ### Francisco Manuel da Silva Gomes
- ### José Arthur Souza Aprigio de Carvalho
- ### Rawlyson Oliveira de Macedo