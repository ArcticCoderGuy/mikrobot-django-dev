# 📚 MikroBot QA Dashboard - Käyttöohjeet

**Kehittäjä:** Markus Kaprio / Fox-In-The-Code  
**Päivitetty:** 2025-07-18

---

## 🎯 Mikä tämä on?

MikroBot QA Dashboard on interaktiivinen testaustyökalu, joka varmistaa että koko MikroBot-järjestelmä toimii moitteettomasti ennen tuotantoon viemistä. Se testaa kaikki kriittiset osat: MCP → Django → LLM → MT5.

---

## 🚀 Pikastart

1. **Avaa Dashboard selaimessa:**
   ```
   file:///C:/Users/HP/Desktop/Claude%20projects/mikrobot_django_dev/mikrobot_qa_dashboard.html
   ```

2. **Seuraa testejä ylhäältä alas** (järjestys on tärkeä!)

3. **Klikkaa testiä** avataksesi yksityiskohdat

4. **Merkitse Pass/Fail** kunkin testin kohdalla

---

## 📋 Testialueet

### 1️⃣ **Ympäristön Valmistelu** 🔧
- Luo `.env` tiedosto MT5-tunnuksilla
- Käynnistä Django-palvelin
- Käynnistä MCP-palvelin

### 2️⃣ **MT5 Yhteys** 📡
- Testaa MetaTrader 5 -yhteys
- Varmista symbolien saatavuus

### 3️⃣ **Signaalin Käsittely** 📨
- Luo testisignaali
- Hyväksy signaali käsittelyä varten

### 4️⃣ **Kaupan Suoritus** 💹
- Avaa kauppa MT5:ssä
- Varmista kauppa MetaTraderissa
- Sulje kauppa

### 5️⃣ **REST API Testit** 🌐
- Testaa API-endpointit
- Varmista autentikointi

### 6️⃣ **End-to-End Testi** 🔄
- Koko prosessin läpikäynti

---

## 🎮 Käyttöohjeet

### **Testin suorittaminen:**

1. **Klikkaa testin nimeä** avataksesi sen
2. **Lue ohjeet** huolellisesti
3. **Kopioi komennot** suoraan dashboardista
4. **Merkitse checkboxit** kun olet suorittanut vaiheen
5. **Paina Pass/Fail** -nappia tuloksen mukaan

### **Pass/Fail -merkinnät:**

- ✅ **Pass** = Testi onnistui täysin
- ❌ **Fail** = Testissä oli ongelmia
- ⏳ **Pending** = Testiä ei ole vielä suoritettu

### **Edistymispalkki:**

Dashboard näyttää reaaliaikaisesti:
- Kuinka monta % testeistä on suoritettu
- Onnistumisprosentti
- Jäljellä olevat testit

---

## 🛠️ Erikoistoiminnot

### **📥 Vie Tulokset**
Tallentaa testien tulokset JSON-tiedostoon:
```json
{
  "testDate": "2025-01-18T10:30:00",
  "tests": {
    "env-setup": "pass",
    "django-server": "pass",
    ...
  },
  "summary": {
    "total": 12,
    "passed": 10,
    "failed": 2
  }
}
```

### **📊 Luo Raportti**
Generoi Markdown-muotoisen testiraportin:
- Yhteenveto tuloksista
- Lista epäonnistuneista testeistä
- Suositukset korjauksille

### **🔄 Nollaa Testit**
Aloittaa testauksen alusta:
- Tyhjentää kaikki merkinnät
- Nollaa edistymispalkin
- Säilyttää debug-lokin

### **🐛 Debug Konsoli**
Näyttää reaaliaikaisesti:
- Testien suoritusajat
- Pass/Fail -merkinnät
- Järjestelmän tapahtumat

---

## 💡 Vinkit

### **Ympäristömuuttujat (.env):**
```env
MT5_LOGIN=123456
MT5_PASSWORD=salasanasi
MT5_SERVER=ICMarkets-Demo03
```

### **Django Shell -komennot:**
```python
# MT5-yhteyden testaus
from trading.mt5_executor import MT5Executor
with MT5Executor() as executor:
    account = executor.get_account_info()
    print(f"Tili: {account['login']}, Saldo: {account['balance']}")
```

### **Testisignaalin luonti:**
```python
from signals.models import MQL5Signal
from decimal import Decimal
import uuid

signal = MQL5Signal.objects.create(
    source_name="TEST",
    symbol="EURUSD",
    direction="BUY",
    entry_price=Decimal("1.0850"),
    stop_loss=Decimal("1.0800"),
    take_profit=Decimal("1.0900")
)
```

---

## 🚨 Yleisimmät Ongelmat

### **MT5 ei yhdisty:**
- Tarkista .env tiedoston tunnukset
- Varmista että MetaTrader 5 on asennettu
- Tarkista palvelimen nimi (esim. ICMarkets-Demo03)

### **Django ei käynnisty:**
- Aktivoi virtuaaliympäristö: `venv\Scripts\activate`
- Asenna riippuvuudet: `pip install -r requirements.txt`
- Aja migraatiot: `python manage.py migrate`

### **API-testit epäonnistuvat:**
- Varmista autentikointi-token
- Tarkista että Django-palvelin on käynnissä
- Katso CORS-asetukset

---

## 📝 Testauksen Checklist

Ennen tuotantoon siirtoa varmista:

- [ ] Kaikki testit PASS-tilassa
- [ ] MT5-yhteys toimii vakaasti
- [ ] Kaupat avautuvat/sulkeutuvat oikein
- [ ] API vastaa alle 500ms
- [ ] Virheloki on tyhjä
- [ ] Raportti generoitu ja tallennettu

---

## 🎉 Testaus Valmis!

Kun kaikki testit näyttävät vihreää:
1. **Generoi loppuraportti** 
2. **Tallenna tulokset**
3. **MikroBot on valmis tuotantoon!**

---

## 💬 Tuki

Jos törmäät ongelmiin testauksen aikana:
1. Tarkista debug-konsoli virheviesteistä
2. Lue läpi yllä olevat vianmääritysvinkit
3. Kysy apua Claude Codelta!

---

**Happy Testing! 🚀**

*- MikroBot QA Dashboard*