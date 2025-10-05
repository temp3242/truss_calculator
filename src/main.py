# python
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
from matplotlib.pyplot import annotate

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


def read_vertices(f, count: int) -> tuple[list[Vertex], list[str]]:
    vertices: list[Vertex] = []
    labels: list[str] = []
    for _ in range(count):
        params = f.readline().rstrip().split("; ")
        labels.append(params[0])
        vertices.append(Vertex(float(params[1]), float(params[2])))
    return vertices, labels


def add_node_labels(ax, vertices: list[Vertex], labels: list[str]) -> None:
    # Hide anaStruct default numeric node labels if present
    for t in list(ax.texts):
        txt = t.get_text().strip()
        if txt.isdigit():
            t.set_visible(False)
    # Overlay custom labels at node coordinates
    for v, lab in zip(vertices, labels):
        ax.annotate(
            lab,
            (v.x, v.y),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=10,
            color="black",
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5),
            zorder=10,
        )

ss = SystemElements()

def main() -> None:
    # Verificando se o arquivo de especificações existe
    spec_path = find("especificacoes.txt", path)
    if spec_path is None:
        print("Arquivo 'especificacoes.txt' não encontrado.")
        return

    with open(spec_path) as f:

        # Garantindo que o diretório de saída exista
        ensure_out_dir(OUTPUT)

        non_free_pins = []
        node_ids = []

        # Lendo o número de nós (vértices)
        line = f.readline().rstrip()
        vertices_num = list(map(int, line.split('; ')))[0]

        # Criando os nós (vértices) e rótulos
        vertices, labels = read_vertices(f, vertices_num)

        # Lendo as especificações do material
        line = f.readlines()
        young_modulus = float(line[vertices_num * 3])
        diameter = float(line[vertices_num * 3 + 1])
        cross_section_area = math.pi * (diameter / 2) ** 2
        ea = young_modulus * cross_section_area
        moment_of_inertia = (math.pi / 4) * (diameter / 2)**4
        ei = young_modulus * moment_of_inertia

        # Criando os elementos (ligações entre os nós)
        # (nesse caso, os elemento são do tipo treliça, pois não há tranmissão de momento)
        for i in range(vertices_num):
            connections = list(map(int, line[i].rstrip().split('; ')))
            for j in range(i + 1, vertices_num):
                if connections[j] == 1:
                    ss.add_truss_element([vertices[i], vertices[j]], EA=ea)

        for v in vertices:
            node_ids.append(ss.find_node_id(v))

        # Adicionando as forças nos nós
        for i in range(vertices_num):
            force_line = list(map(float, line[i + vertices_num].rstrip().split('; ')))
            if force_line[0] != 0 and force_line[1] != 0:
                ss.point_load(node_ids[i], Fx=force_line[0], Fy=force_line[1])
            elif force_line[0] != 0:
                ss.point_load(node_ids[i], Fx=force_line[0])
            elif force_line[1] != 0:
                ss.point_load(node_ids[i], Fy=force_line[1])

        # Adicionando os vículos dos nós (tipos de apoio)
        # Os tipos podem ser: Nó Livre, Pino, Rolete e Apoio Lateral
        for i in range(vertices_num):
            pin_type = line[i + vertices_num * 2].rstrip()
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
            out_folder = os.path.join(path, "out")

            # Estrutura
            ss.show_structure(show=False)
            ax = plt.gca()
            add_node_labels(ax, vertices, labels)
            plt.title('Estrutura')
            plt.savefig(out_folder + '/estrutura.png')
            plt.close('all')

            # Forças de reação
            ss.show_reaction_force(show=False)
            ax = plt.gca()
            add_node_labels(ax, vertices, labels)
            plt.title('Forças de Reação')
            plt.savefig(out_folder + '/reacao.png')
            plt.close('all')

            # Forças axiais
            ss.show_axial_force(show=False)
            ax = plt.gca()
            add_node_labels(ax, vertices, labels)
            plt.title('Forças axiais')
            plt.savefig(out_folder + '/forcas_axiais.png')
            plt.close('all')

            # Deslocamento
            ss.show_displacement(show=False)
            ax = plt.gca()
            add_node_labels(ax, vertices, labels)
            plt.title('Deslocamento')
            plt.savefig(out_folder + '/deslocamento.png')
            plt.close('all')

            # Deformação (Momento fletor)
            ss.show_bending_moment(show=False)
            ax = plt.gca()
            add_node_labels(ax, vertices, labels)
            plt.title('Deformação (Momento Fletor)')
            plt.savefig(out_folder + '/deformacao.png')
            plt.close('all')

        # Printando as forças nos nós/apoios não-livres
        print("Forças de reação:")
        for v in non_free_pins:
            results = ss.get_node_results_system(v)
            print(f"  Nó {v}: Fx={round(-results['Fx'], 1) + 0}; Fy={round(-results['Fy'], 1) + 0}")

        # Printando as forças internas dos elementos
        print("\nForças internas:")
        results = ss.get_element_results()
        for e in results:
            alpha = e['alpha']
            N = -float(e['Nmin'])  # ou Nmax

            Fx = N * math.cos(alpha)
            Fy = N * math.sin(alpha)

            print(f"  Elemento {e['id']}: Fx={round(Fx, 1) + 0}; Fy={round(Fy, 1) + 0}; N={round(-N, 1) + 0}")

        # Printando os deslocamentos nos nós
        print("\nDeslocamentos:")
        for i in range(1, vertices_num + 1):
            displacement = ss.get_node_displacements(i)
            print(f"  Nó {labels[i-1]}: dx={displacement['ux']:.5f}; dy={displacement['uy']:.5f}")


if __name__ == "__main__":
    main()