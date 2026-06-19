import pandas as pd

# carrega o CSV e salva como parquet q eh um formato mais leve e rapido d ler pro streamlit nao travar pq o csv e grande
df = pd.read_csv("data/anime_dataset_final.csv")
df.to_parquet("data/anime_dataset_final.parquet", index=False)
print("Sucesso! Pode deletar o CSV se quiser.")