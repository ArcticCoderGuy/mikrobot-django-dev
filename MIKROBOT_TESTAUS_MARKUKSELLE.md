# 🚀 MikroBot Testausohje - Markukselle

**Tervetuloa testaamaan MikroBot-järjestelmääsi!**  
Tämä ohje on kirjoitettu juuri sinulle - selkeästi ja käytännönläheisesti.

---

## 📋 Mitä tässä testataan?

MikroBot on monimutkainen järjestelmä, joka yhdistää:
- **MetaTrader 5** (kaupankäyntialusta)
- **Django** (web-sovellus)
- **MCP** (signaalien käsittely)
- **LLM** (tekoäly-analyysi)

Dashboard varmistaa, että kaikki nämä osat toimivat yhdessä saumattomasti.

---

## 🎯 Lean-ajattelu testauksessa

Kuten Lean-filosofiassa:
1. **Eliminoi hukka** - Testaa vain kriittiset asiat
2. **Jatkuva parantaminen** - Jokainen testi opettaa jotain
3. **Visualisoi prosessi** - Dashboard näyttää missä mennään
4. **Stop & Fix** - Jos testi epäonnistuu, korjaa ennen jatkamista

---

## 📝 Näin aloitat (Step-by-Step)

### 1️⃣ **Valmistelut (5 min)**

Avaa kolme komentoriviä (Command Prompt):

**Komentorivissä 1 - Django:**
```bash
cd "C:\Users\HP\Desktop\Claude projects\mikrobot_django_dev"
venv\Scripts\activate
python manage.py runserver
```
→ Pitäisi näkyä: "Starting development server at http://127.0.0.1:8000/"

**Komentorivissä 2 - MCP:**
```bash
cd "C:\Users\HP\Desktop\Claude projects\mikrobot-mcp-dev"
venv\Scripts\activate
python main.py
```
→ Pitäisi näkyä: "MCP Server started on port 6789"

**Komentorivissä 3 - jätä auki testejä varten**

### 2️⃣ **Dashboard käyttö**

1. **Klikkaa testiä** → Avautuu ohjeet
2. **Lue mitä tehdään** → Ymmärrä ennen tekemistä
3. **Kopioi komennot** → Liitä komentoriville
4. **Merkitse tulos:**
   - ✅ **Toimii** = Kaikki meni hyvin
   - ❌ **Ei toimi** = Jotain meni pieleen

---

## 🔍 Testien selitykset

### **1. Ympäristön Valmistelu** 🔧

**MT5 Ympäristömuuttujat:**
- Luo `.env` tiedosto Django-kansioon
- Lisää sinne MT5-tilisi tiedot:
```
MT5_LOGIN=sinun_tilinumero
MT5_PASSWORD=sinun_salasana
MT5_SERVER=välittäjäsi_palvelin
```

💡 **Vinkki:** Jos et tiedä palvelimen nimeä, katso MetaTrader 5:stä:
Tiedosto → Avaa tili → Valitse välittäjä → Näet palvelimen nimen

### **2. MT5 Yhteys** 📡

Tässä testataan, että ohjelma saa yhteyden MetaTraderiin.

**Python Shell -testi:**
```python
# Komentorivillä 3:
cd "C:\Users\HP\Desktop\Claude projects\mikrobot_django_dev"
venv\Scripts\activate
python manage.py shell

# Kopioi nämä rivit yksi kerrallaan:
from trading.mt5_executor import MT5Executor
executor = MT5Executor()
executor.connect()
```

Jos näet "MT5 connected successfully" → Merkitse ✅ Toimii

### **3. Signaalin Käsittely** 📨

Luodaan "feikki" kaupankäyntisignaali testausta varten:

```python
# Jatka samassa Python shellissä:
from signals.models import MQL5Signal
from decimal import Decimal

# Luo testisignaali
signal = MQL5Signal.objects.create(
    source_name="TESTI",
    symbol="EURUSD",
    direction="BUY",
    entry_price=Decimal("1.0850"),
    stop_loss=Decimal("1.0800"),
    take_profit=Decimal("1.0900")
)
print(f"Signaali luotu: {signal.id}")

# Hyväksy se
signal.status = 'approved'
signal.save()
```

### **4. Kaupan Suoritus** 💹

**VAROITUS:** Tämä avaa oikean kaupan MT5:ssä! Käytä demo-tiliä!

```python
# Suorita kauppa (0.01 lot = pienin mahdollinen)
from trading.mt5_executor import execute_approved_signal
success, viesti, ticket = execute_approved_signal(str(signal.id), Decimal("0.01"))
print(viesti)
```

Tarkista MetaTrader 5:stä että kauppa näkyy.

---

## ❓ Yleisimmät ongelmat

### "MT5 initialization failed"
- Tarkista että MetaTrader 5 on auki
- Varmista .env tiedoston tiedot
- Kokeile toista palvelinta (esim. ICMarkets-Demo02)

### "Symbol EURUSD not found"
- Avaa MT5 → Market Watch → Oikea klikkaus → Show All
- Etsi EURUSD ja tuplaklikkkaa

### "Django ei käynnisty"
```bash
# Asenna paketit uudelleen:
pip install -r requirements.txt
python manage.py migrate
```

---

## 💪 Rohkaisua

**Muista:**
- Jokainen virhe on oppimistilaisuus
- Et voi rikkoa mitään pysyvästi (paitsi demo-tilin saldon 😄)
- Dashboard tallentaa edistymisen - voit jatkaa myöhemmin
- Lean-periaate: "Go and See" - kokeile rohkeasti!

**50-vuotiaana aloittavana kehittäjänä** sinulla on etu:
- Ymmärrät prosessit (Lean-tausta)
- Osaat priorisoida (mikä on tärkeää)
- Et pelkää kysyä apua

---

## 🎉 Kun kaikki testit ovat vihreitä

1. **Paina "Luo Raportti"** - Saat dokumentin testauksesta
2. **Juhli hetki** - Olet saanut monimutkaisen systeemin toimimaan!
3. **Seuraava askel** - Voit alkaa kehittää omia ideoitasi

---

## 📞 Tuki

Jos jumitut:
1. Lue Debug-konsolia (alhaalla dashboardissa)
2. Google virheilmoitukset - joku on törmännyt samaan
3. Kysy Claude Codelta - "Miten korjaan tämän virheen: [virheilmoitus]"

---

**Tsemppiä testaukseen, Markus! Tämä on hieno järjestelmä jonka olet rakentanut. 💪**

*PS. Ideoita on hyvä olla 100x enemmän kuin taitoa - se on merkki luovuudesta. Taito tulee tekemällä!*