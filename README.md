# 🎬 Anime Analytics Dashboard

Dashboard interativo construído com **Streamlit + Plotly**, a partir das análises feitas em
`PM04_Storytelling.ipynb`. Mantém a mesma identidade visual do notebook (fundo escuro,
acentos em rosa/roxo) e transforma cada pergunta analítica do projeto em um gráfico
filtrável: gêneros, estúdios, episódios, década, popularidade e engajamento.

## O que o dashboard tem

- **Filtros na barra lateral**: período (ano de lançamento), gênero, estúdio, tipo,
  classificação etária, faixa de score e faixa de episódios.
- **Chips de "filtros ativos"** no topo, mostrando exatamente o que está sendo aplicado.
- **KPIs** (cards): total de animes, score médio, total de membros, total de favoritos
  e gênero mais frequente — todos recalculados conforme os filtros.
- **4 abas**: Visão Geral (evolução por década + episódios), Gêneros & Estúdios,
  Distribuição & Engajamento, e Dados (tabela + download do CSV filtrado).
- Botão **"Limpar filtros"**.

---

## Passo a passo (VSCode)

### 1. Estrutura de pastas
Você já recebeu a estrutura pronta. Deve ficar assim:

```
anime_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── data/
    └── anime_dataset_final.csv   ← meninas vocês precisam colocar este arquivo aqui
```

### 2. Abra a pasta no VSCode
`File > Open Folder...` e selecione `anime_dashboard`.
Recomendo instalar a extensão **Python** (Microsoft) se ainda não tiver.

### 3. Crie um ambiente virtual
Abra o terminal integrado do VSCode (`` Ctrl+` ``) e rode:

```bash
python -m venv venv
```

Ative o ambiente:

- **Windows (PowerShell)**: `venv\Scripts\Activate.ps1`
- **Windows (cmd)**: `venv\Scripts\activate.bat`
- **macOS / Linux**: `source venv/bin/activate`

No canto inferior direito do VSCode, confirme que o interpretador selecionado é o do
`venv` (clique no nome do interpretador na barra de status e escolha o do `venv` se
não tiver sido detectado automaticamente).

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Coloque sua base de dados
Copie o arquivo `anime_dataset_final.csv` (o mesmo do Google Drive usado no Colab)
para dentro de `data/`. Se não fizer isso, o próprio app vai te pedir para enviar o
CSV pela barra lateral assim que abrir.

### 6. Rode o dashboard

Primeiro, você precisa verificar o `arquivo converter.py`, na pasta onde ele estiver rode: `python converter.py`. Estamos convertendo o csv para parquer, assim não fica tão pesado e roda mais fácil no streamlit.
Depois você pode iniciar a aplicação: `python -m streamlit run app.py`


```bash
streamlit run app.py
```

Isso abre automaticamente `http://localhost:8501` no navegador. Para parar, `Ctrl+C`
no terminal.

---


## Caso suas colunas tenham nomes diferentes

O app espera as colunas usadas no notebook original: `title`, `type`, `episodes`,
`release_start`, `rating`, `score`, `genres` (separado por `|`), `studios` (separado
por `|`), `members`, `favorites`, `decade`, `engagement_ratio_pct`. Se algum nome for
diferente na sua base, ajuste as referências correspondentes em `app.py` (cada gráfico
já tem uma verificação `if "coluna" not in df.columns` que evita quebrar o app —
mas exibirá um aviso ao invés do gráfico).

