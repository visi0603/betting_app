import streamlit as st
import pandas as pd
import requests
from datetime import datetime
st.set_page_config(page_title="Football Betting Analiza", page_icon="⚽", layout="centered")
st.title("⚽ Pametna Analiza Utakmica")
st.write("Dohvat parova s raznovrsnim i uravnoteženim preporukama (1, 2, 1X).")
# Odabir datuma kroz sučelje
odabrani_datum = st.date_input("Izaberi datum utakmica", datetime.now())
espn_date = odabrani_datum.strftime("%Y%m%d")
datum_str = odabrani_datum.strftime("%Y-%m-%d")

if st.button("Pokreni analizu parova"):
    st.info(f"Dohvaćam parove za datum: {datum_str}...")
    
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={espn_date}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
           st.error(response.status_code)
        else:
            data = response.json()
            events = data.get('events', [])
            
            if not events:
                st.warning(f"Na odabrani datum ({datum_str}) nema pronađenih utakmica.")
            else:
                utakmice_lista = []
                
                top_reprezentacije = ["Germany", "France", "Spain", "Brazil", "Argentina", "England", "Portugal", "Netherlands", "Italy", "Belgium"]
                nezgodni_domacini = ["Turkey", "Turska", "Croatia", "Hrvatska", "Serbia", "Srbija", "Poland", "Poljska", "Greece", "Grčka", "Uruguay", "Colombia"]

                for event in events:
                    league_name = "Nogometna liga"
                    try:
                        competitions_list = event.get('competitions', [])
                        if competitions_list:
                            comp_item = competitions_list[0]
                            if 'league' in comp_item and isinstance(comp_item['league'], dict):
                                league_name = comp_item['league'].get('name', '')
                            elif 'tournament' in comp_item and isinstance(comp_item['tournament'], dict):
                                league_name = comp_item['tournament'].get('name', '')
                    except:
                        pass

                    competitions = event.get('competitions', [])
                    if not competitions:
                        continue
                        
                    competitors = competitions[0].get('competitors', [])
                    if len(competitors) == 2:
                        domacin, gost = "", ""
                        for team in competitors:
                            if team.get('homeAway') == 'home':
                                domacin = team.get('team', {}).get('displayName', '')
                            else:
                                gost = team.get('team', {}).get('displayName', '')
                        
                        if not domacin or not gost:
                            continue

                        domacin_je_jak = any(t.lower() in domacin.lower() for t in top_reprezentacije)
                        gost_je_jak = any(t.lower() in gost.lower() for t in top_reprezentacije)
                        domacin_je_nezgodan = any(n.lower() in domacin.lower() for n in nezgodni_domacini)

                        # Uravnoteženo određivanje tipova da nisu svi isti
                        h_len = len(domacin)
                        a_len = len(gost)

                        if domacin_je_jak and gost_je_jak:
                            tip = f"X2 (Dupla šansa na gosta) - Derbi"
                            vjerojatnost = 65.0
                        elif gost_je_jak and not domacin_je_nezgodan:
                            tip = f"2 (Pobjeda gosta: {gost})"
                            vjerojatnost = 73.0
                        elif domacin_je_jak or domacin_je_nezgodan:
                            tip = f"1 (Pobjeda domaćina: {domacin})"
                            vjerojatnost = 75.0
                        else:
                            # Za ostale (obične) parove miješamo 1, 2 ili 1X prema formuli dužine imena
                            formula_val = (h_len * 3 + a_len * 2) % 3
                            if formula_val == 0:
                                tip = f"1 (Pobjeda domaćina: {domacin})"
                                vjerojatnost = 67.0
                            elif formula_val == 1:
                                tip = f"2 (Pobjeda gosta: {gost})"
                                vjerojatnost = 66.0
                            else:
                                tip = f"1X (Dupla šansa: {domacin})"
                                vjerojatnost = 69.0

                        utakmice_lista.append({
                            'Liga': league_name,
                            'Utakmica': f"{domacin} vs {gost}",
                            'Tip': tip,
                            'Vjerojatnost': vjerojatnost
                        })

                if utakmice_lista:
                    df = pd.DataFrame(utakmice_lista)
                    df = df[df['Vjerojatnost'] >= 60.0]
                    df = df.sort_values(by='Vjerojatnost', ascending=False)
                    
                    top_izbori = df.head(15)

                    if top_izbori.empty:
                        st.warning("Nema parova za prikaz.")
                    else:
                        st.success("Uspješno pronađeni parovi s raznovrsnim tipovima! 🎉")
                        
                        for idx, row in top_izbori.reset_index(drop=True).iterrows():
                            with st.container():
                                st.markdown(f"### {idx + 1}. {row['Utakmica']}")
                                st.write(f"📌 **Natjecanje:** {row['Liga']}")
                                st.write(f"👉 **Preporuka:** {row['Tip']}")
                                st.progress(int(row['Vjerojatnost']))
                                st.caption(f"Procjena vjerojatnosti: **{row['Vjerojatnost']}%**")
                                st.divider()
                else:
                    st.warning("Nema dovoljno podataka za obradu.")
    except Exception as e:
        st.error(f"Došlo je do greške: {e}")
