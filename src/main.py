# Truss Calculator
#
# Por: Arthur Gaudêncio, Francisco Manuel, Gabriel Araújo, José Arthur e Rawlyson Macedo
#
# Para a disciplina de Mecânica para Engenharia da Computação
#
# Professor Hugo Cavalcante

# Centro de Informática (CI) - UFPB - 2025.1


import math
import os
from pathlib import Path

import matplotlib.pyplot as plt
from anastruct import SystemElements, Vertex

OUTPUT = True  # Set to False to skip creating visualizations
path = Path(__file__).parent.parent.resolve()

def ensure_out_dir(enabled: bool) -> None:
    if enabled:
        Path(str(os.path.join(path, "out"))).mkdir(parents=True, exist_ok=True)


def find(name: str, search_path: str) -> str | None:
    for root, _, files in os.walk(search_path):
        if name in files:
            return os.path.join(root, name)
    return None


def read_vertices(f, count: int) -> list[Vertex]:
    vertices: list[Vertex] = []
    for _ in range(count):
        params = f.readline().rstrip().split("; ")
        vertices.append(Vertex(float(params[1]), float(params[2])))
    return vertices

ss = SystemElements()

def main() -> None:
    # Verificando se o arquivo de especificações existe
    if find("especificacoes.txt", path) is None:
        print("Arquivo 'especificacoes.txt' não encontrado.")
        return
    
    with open(find("especificacoes.txt", path)) as f:
        
        # Garantindo que o diretório de saída exista
        ensure_out_dir(OUTPUT)
        
        non_free_pins = []
        node_ids = []

        # Lendo o número de nós (vértices)
        line = f.readline().rstrip()
        vertices_num = list(map(int, line.split('; ')))[0]

        # Criando os nós (vértices)
        vertices = read_vertices(f, vertices_num)
        
        # Criando os elementos (ligações entre os nós)
        # (nesse caso, os elemento são do tipo treliça, pois não há tranmissão de momento)
        for i in range(vertices_num):
            line = list(map(int, f.readline().rstrip().split('; ')))
            for j in range(i + 1, vertices_num):
                if line[j] == 1:
                    ss.add_truss_element([vertices[i], vertices[j]])
                    
        for v in vertices:
            node_ids.append(ss.find_node_id(v))

        # Adicionando as forças nos nós
        for i in range(vertices_num):
            line = list(map(float, f.readline().rstrip().split('; ')))
            if line[0] != 0 and line[1] != 0:
                ss.point_load(node_ids[i], Fx=line[0], Fy=line[1])
            elif line[0] != 0:
                ss.point_load(node_ids[i], Fx=line[0])
            elif line[1] != 0:
                ss.point_load(node_ids[i], Fy=line[1])

        # Adicionando os vículos dos nós (tipos de apoio)
        # Os tipos podem ser: Nó Livre, Pino, Rolete e Apoio Lateral
        for i in range(vertices_num):
            pin_type = f.readline().rstrip()
            if pin_type == 'P':
                ss.add_support_hinged(node_ids[i])
                non_free_pins.append(node_ids[i])
            elif pin_type == 'X':
                ss.add_support_roll(node_ids[i], direction=1)
                non_free_pins.append(node_ids[i])
            elif pin_type == 'Y':
                ss.add_support_roll(node_ids[i], direction=2)
                non_free_pins.append(node_ids[i])

        
        ss.solve(max_iter=10000)

        if OUTPUT:
            # Visualização da estrutura com a(s) força(s) aplicada(s)
            
            out_folder = os.path.join(path, "out")
            
            ss.show_structure(show=False)
            plt.title('Estrutura')
            plt.savefig(out_folder + '/estrutura.png')
            plt.close('all')

            # Visualização das forças de reação
            ss.show_reaction_force(show=False)
            plt.title('Forças de Reação')
            plt.savefig(out_folder + '/reacao.png')
            plt.close('all')

            # Visualização das forças axiais
            ss.show_axial_force(show=False)
            plt.title('Forças axiais')
            plt.savefig(out_folder + '/forcas_axiais.png')
            plt.close('all')

            # Visualização do deslocamento
            ss.show_displacement(show=False)
            plt.title('Deslocamento')
            plt.savefig(out_folder + '/deslocamento.png')
            plt.close('all')

        # Printando as forças nos nós/apoios não-livres
        for v in non_free_pins:
            results = ss.get_node_results_system(v)
            print(f'{round(-results['Fx'], 1) + 0}; {round(-results['Fy'], 1) + 0}')

        # Pritando as forças internas dos elementos
        results = ss.get_element_results()
        for e in results:
            alpha = e['alpha']
            N = -float(e['Nmin'])  # ou Nmax

            Fx = N * math.cos(alpha)
            Fy = N * math.sin(alpha)

            print(f"{round(Fx, 1) + 0}; {round(Fy, 1) + 0}; {round(-N, 1) + 0}")
            
if __name__ == "__main__":
    main()
