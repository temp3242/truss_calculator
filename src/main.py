# Truss Calculator
#
# Por: Arthur Gaudêncio, Francisco Manuel, Gabriel Araújo, José Arthur e Rawlyson Macedo
#
# Para a disciplina de Mecânica para Engenharia da Computação
#
# Professor Hugo Cavalcante

# Centro de Informática (CI) - UFPB - 2025.1


from anastruct import SystemElements, Vertex
import matplotlib.pyplot as plt
from anastruct.fem.plotter import element
import math
import os

from pathlib import Path

path = Path.cwd().parent

output = True  # Caso não se deseje a criação das visualizações do sistema, mude a variável para "False"

if output:
    Path("../out").mkdir(parents=True, exist_ok=True)


# Função para achar um arquivo em um determinado diretório
def find(name: str, path: str) -> str:
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


ss = SystemElements()

with open(find("especificacoes.txt", path)) as f:
    vertices = []
    non_free_pins = []

    line = f.readline().rstrip()
    vertices_elements_num = list(map(int, line.split('; ')))

    # Lendo o número de nós (apoios) e elementos
    for _ in range(vertices_elements_num[0]):
        params = f.readline().rstrip().split('; ')
        vertices.append(Vertex(float(params[1]), float(params[2])))

    # Criando os elementos (ligações entre os nós)
    # (nesse caso, os elemento são do tipo treliça, pois não há tranmissão de momento)
    for i in range(len(vertices)):
        line = list(map(int, f.readline().rstrip().split('; ')))
        for j in range(i + 1, len(vertices)):
            if line[j] == 1:
                ss.add_truss_element([vertices[i], vertices[j]])

    # Adicionando as forças nos nós
    for v in vertices:
        line = list(map(float, f.readline().rstrip().split('; ')))
        if line[0] != 0:
            ss.point_load(ss.find_node_id(v), Fx=line[0])
        if line[1] != 0:
            ss.point_load(ss.find_node_id(v), Fy=line[1])

    # Adicionando os vículos dos nós (tipos de apoio)
    # Os tipos podem ser: Nó Livre, Pino, Rolete e Apoio Lateral
    for v in vertices:
        pin_type = f.readline().rstrip()
        if pin_type == 'P':
            ss.add_support_hinged(ss.find_node_id(v))
            non_free_pins.append(ss.find_node_id(v))
        elif pin_type == 'X':
            ss.add_support_roll(ss.find_node_id(v), direction=1)
            non_free_pins.append(ss.find_node_id(v))
        elif pin_type == 'Y':
            ss.add_support_roll(ss.find_node_id(v), direction=2)
            non_free_pins.append(ss.find_node_id(v))

    #
    ss.solve(max_iter=10000)

    if output:
        # Visualização da estrutura com a(s) força(s) aplicada(s)
        ss.show_structure(show=False)
        plt.title('Estrutura')
        plt.savefig('../out/estrutura.png')

        # Visualização das forças de reação
        ss.show_reaction_force(show=False)
        plt.title('Forças de Reação')
        plt.savefig('../out/reacao.png')

        # Visualização das forças axiais
        ss.show_axial_force(show=False)
        plt.title('Forças axiais')
        plt.savefig('../out/forcas_axiais.png')

        # Visualização do deslocamento
        ss.show_displacement(show=False)
        plt.title('Deslocamento')
        plt.savefig('../out/deslocamento.png')

    # Printando as forças nos nós/apoios não-livres
    for v in non_free_pins:
        results = ss.get_node_results_system(v)
        print(f'{round(results['Fx'], 1) + 0}; {round(results['Fy'], 1) + 0}')

    # Pritando as forças internas dos elementos
    results = ss.get_element_results()
    for e in results:
        alpha = e['alpha']
        N = -float(e['Nmin'])  # ou Nmax

        Fx = N * math.cos(alpha)
        Fy = N * math.sin(alpha)

        print(f"{Fx:.1f}; {Fy:.1f}; {N:.1f}")

    # Fechando o arquivo "especificacoes.txt"
    f.close()
