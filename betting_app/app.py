import pandas as pd 
import requests 
 
data = { 
    "Utakmica": ["Arsenal - Chelsea", "Real Madrid - Barcelona", "Inter - Milan"], 
    "Koef_1": [1.90, 2.10, 1.80], 
    "Koef_X": [3.40, 3.50, 3.40], 
    "Koef_2": [4.00, 3.20, 4.50], 
    "Forma_Domacin": [85, 60, 90], 
    "Forma_Gost": [50, 65, 60] 
} 
df = pd.DataFrame(data) 
 
# Izracun vjerojatnosti na temelju forme (Matematicki model) 
df['Ukupna_Forma'] = df['Forma_Domacin'] + df['Forma_Gost'] 
df['Sanse_Domacin_Pct'] = (df['Forma_Domacin'] / df['Ukupna_Forma']) * 100 
df['Implied_Prob_1'] = (1 / df['Koef_1']) * 100 
 
# Pronalazenje vrijednosnih parova (gdje su nase sanse vece od kladionice) 
df['Value_Razlika'] = df['Sanse_Domacin_Pct'] - df['Implied_Prob_1'] 
df['Preporuka'] = df['Value_Razlika'].apply(lambda x: 'IGRAJ (Value)' if x > 0 else 'Izbjegavaj') 
 
print("--- ANALIZA I MATEMATICKI NAJSIGURNIJI PAROVI ---") 
print(df[['Utakmica', 'Koef_1', 'Sanse_Domacin_Pct', 'Value_Razlika', 'Preporuka']]) 
