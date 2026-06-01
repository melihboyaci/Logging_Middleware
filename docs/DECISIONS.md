# DECISIONS - Mimari Karar Kayitlari (ADR)

Yeni karar alindiginda en uste yeni madde eklenir. Eski kararlar **silinmez**, gerekirse "Superseded by D-XYZ" notu ile guncellenir.

---

## D-003 (2026-06-01) - 5 tasarim kalibi kullanilacak (minimum 3)

**Baglam.** Odev en az 3 tasarim kalibi istiyor. Notlar minimumun 3 oldugunu dogruluyor.

**Karar.** 5 kalip kullanilir: **Chain of Responsibility** (pipeline), **Strategy** (formatlayicilar), **Decorator** (zenginlestirme), **Factory** (log + formatter uretimi), **Singleton** (metrik/konfig).

**Gerekce.** Pipeline icin CoR dogal; bicimlendirme icin Strategy ders kitabi ornegi; zenginlestirme aslen Decorator'un canli ornegi. Factory ve Singleton minimum maliyetle iki kalip daha ekliyor; raporda her birinin "nerede ve neden" anlatimi guclu.

**Sonuc.** Yerleri `docs/SPECS.md` boluum 7'de tabloda.

---

## D-002 (2026-06-01) - Tum cikti formatlari implementli; rol->format eslemesi konfigure edilebilir

**Baglam.** Odev metni HTML/CSV/JSON; el yazisi notlar Markdown/JSON/CSV diyor. Iki kaynak celisiyor.

**Karar.** HTML + Markdown + CSV + JSON dortunu de implementlenir (Strategy + Factory). Varsayilan esleme notlardakidir: **sysadmin -> .md**, **developer -> .json**, **security -> .csv**. Esleme `middleware/src/config.py` -> `ROLE_FORMAT_MAP` ile degisebilir.

**Gerekce.** Iki kaynagi da karsilayan ve degistirilebilirligi kalip uzerinden gosteren en saglam yol. Demo videosunda config degistirip yeniden calistirarak Strategy/Factory'nin canli faydasi gosterilebilir.

---

## D-001 (2026-06-01) - Transport: RabbitMQ (HTTP REST yerine)

**Baglam.** Odev "iki docker modulu" ve "yuksek sayida veri ureterek performans araligini olcun" diyor. HTTP REST iki container kisitini birebir karsiliyor ama senkron istek/cevap, gercek throughput olcumunde geri-basinc yaratiyor.

**Karar.** Mesajlasma altyapisi olarak **RabbitMQ** kullanilir (`rabbitmq:3-management` resmi image, ek container).

**Gerekce.**
- Producer ve middleware decoupled olur; gercek **publish-rate**, **consume-rate** ve **queue depth** ayri ayri olculur (raporda guclu grafik).
- "Tum loglari islemedigimizi gostermek" maddesi icin queue-depth + filtre-dusus orani altin standart.
- Borsa/log domaininde gercekci (Kafka/RabbitMQ standart).
- "Iki docker modulu" ifadesi gelistirdigimiz iki uygulama modulu olarak yorumlanir; RabbitMQ standart altyapi bilesenidir (kod yazmiyoruz, resmi image kullaniyoruz). Raporda bir paragrafla gerekcelenir.

**Sonuc.** `docker-compose.yml` 3 servisli (producer, middleware, rabbitmq); `aio-pika` her iki uygulama modulunde.

**Reddedilenler.**
- *HTTP REST*: senkron geri-basinc gercek olcumu bozar.
- *Raw TCP socket*: dusuk seviye, throughput ile riski karsilamiyor.
- *Paylasilan volume / dosya kuyrugu*: gercekci degil, demo zayif kalir.
