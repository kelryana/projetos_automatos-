🤖 Suíte de Simulação de Máquinas de Estados

Um ambiente visual e interativo para simulação de modelos computacionais fundamentais: Autômatos Finitos, Autômatos com Pilha e Máquinas de Turing. Desenvolvido como projeto final para a disciplina de Linguagens Formais e Autômatos.

📋 Sobre o Projeto

Este software tem como objetivo facilitar o estudo da Teoria da Computação, permitindo que estudantes visualizem o comportamento abstrato das máquinas de estados. O sistema implementa visualizações gráficas para a fita infinita da Máquina de Turing, grafos de estados dinâmicos e pilhas de memória.

Módulos Incluídos

Autômatos Finitos (AFD/AFN): Validação de cadeias regulares e conversão de não-determinismo.

Autômatos com Pilha (AP): Simulação de linguagens livres de contexto com suporte a não-determinismo (busca em largura).

Máquina de Turing (MT): Simulação completa de linguagens recursivamente enumeráveis com fita infinita.

✨ Funcionalidades

1. Máquina de Turing (Visual)

Interface Gráfica Completa: Desenho automático do grafo de estados usando NetworkX e Matplotlib.

Fita Infinita: Suporte visual e lógico para fita com alocação dinâmica.

Controles de Execução: Modos Step-by-Step (Passo a Passo), Run (Execução Contínua) e controle de velocidade.

Persistência: Salvar e carregar máquinas em formato .json.

Proteção: Timeout configurável para evitar travamentos em loops infinitos (Halting Problem).

2. Autômatos Finitos

Validação de cadeias para AFD e AFN.

Algoritmo de Subset Construction para conversão automática de AFN para AFD.

Visualização de estados ativos em tempo real (destaque colorido).

3. Autômatos com Pilha

Painel para inserção de regras de transição complexas (Lê, Desempilha, Empilha).

Simulação não-determinística robusta.

Visualização do conteúdo da pilha a cada passo.

🛠️ Tecnologias Utilizadas

O projeto foi construído inteiramente em Python 3, utilizando as seguintes bibliotecas:

Tkinter: Interface Gráfica nativa (GUI).

NetworkX: Cálculos de teoria dos grafos e layout de nós.

Matplotlib: Renderização vetorial dos grafos dentro da interface.


Nota: Os scripts para Autômatos Finitos e Autômatos com Pilha podem ser executados como módulos independentes ou integrados conforme a necessidade.

🚀 Como Executar

Pré-requisitos

Certifique-se de ter o Python 3.x instalado. Você precisará instalar as dependências externas:

pip install networkx matplotlib


Rodando a Simulação

Para iniciar a interface visual da Máquina de Turing:

python main.py


📸 Exemplos de Uso

Configurando uma Máquina de Turing

Abra o programa.

No painel direito, adicione estados (ex: q0, q1).

Defina o estado inicial e os estados de aceitação.

Adicione transições no formato: Origem -> Lê -> Escreve -> Move -> Destino.

Insira a entrada na fita (ex: 1011) e clique em Rodar.

JSON de Exemplo

O sistema aceita importação de arquivos .json. Exemplo de estrutura:

{
  "Q": ["q0", "q1", "q_accept"],
  "sigma": ["0", "1"],
  "gamma": ["0", "1", "λ"],
  "transitions": [
    {"from": "q0", "read": "0", "to": "q0", "write": "0", "move": "R"}
  ]
}

