# Telegram-notifikaatioiden käyttöönotto

## 1. Luo Telegram Bot

1. **Mene Telegramissa:** @BotFather
2. **Aloita keskustelu:** `/start`
3. **Luo uusi bot:** `/newbot`
4. **Anna botti nimi:** `MikroBot QA Monitor`
5. **Anna käyttäjänimi:** `mikrobot_qa_monitor_bot` (tai jokin muu vapaana oleva)
6. **Kopioi Bot Token:** Saat viestin muodossa `Use this token to access the HTTP API: 1234567890:ABCdefGHIjklMNOpqrSTUvwxyz`

## 2. Käynnistä keskustelu bottin kanssa

1. **Etsi botti:** Hae luomasi botti Telegramissa
2. **Paina START:** Aloita keskustelu botilla
3. **Lähetä viesti:** Lähetä mikä tahansa viesti (esim. "Hello")

## 3. Päivitä Bot Token

Korvaa `telegram_notifier.py` tiedostossa:

```python
self.bot_token = "1234567890:ABCdefGHIjklMNOpqrSTUvwxyz"  # Korvaa omalla tokenilla
```

## 4. Testaa yhteys

```cmd
cd "C:\Users\HP\Desktop\Claude projects\mikrobot_django_dev"
python dashboard/telegram_notifier.py
```

## 5. Käynnistä QA-monitorointi uudelleen

Nyt QA-automation lähettää automaattisesti viestejä @ArcticTrader:lle kun:
- ❌ Testien läpäisyprosentti laskee alle 100%
- ⚠️ Jokin komponenti antaa varoituksen
- 🚨 Järjestelmä kaatuu

## Viestin formaatti:

```
🚨 MikroBot QA Alert

⚠️ WARNING: QA Tests below 100%

📊 Results:
• Pass Rate: 85.7%  
• Tests: 6/7
• Failed: 0
• Warnings: 1

🕒 Time: 15:30:25

🔍 Failed Tests:
• end_to_end: WARN - Unexpected response: 401

🖥️ Dashboard: http://localhost:8000/dashboard/
```

## Troubleshooting:

- **403 Forbidden:** Bot ei saa lähettää viestejä → Aloita keskustelu botilla
- **401 Unauthorized:** Väärä bot token → Tarkista token @BotFather:ssa  
- **400 Bad Request:** Chat not found → Varmista että @ArcticTrader on oikein

## Turvallisuus:

⚠️ **ÄLÄ jaa bot tokenia julkisesti!**
- Token on salainen API-avain
- Sen avulla kuka tahansa voi lähettää viestejä bottiisi