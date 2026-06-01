# CENG302 Logging Middleware

RabbitMQ tabanli veri middleware odev projesi.

## Proje Ozeti

Sistem 2 uygulama modulu + 1 altyapi bileseninden olusur:

- Producer (log uretir ve RabbitMQ'ya yayinlar)
- Middleware (loglari anonimlestirir, filtreler, zenginlestirir, role gore formatlayip dosyaya yazar)
- RabbitMQ (mesaj broker)

Pipeline:

`Anonymize -> Filter -> Enrich -> Format/Route`

## Klasorler

- `producer/`: veri uretimi + publisher + stress tools
- `middleware/`: consumer + pipeline + api + metrics
- `shared/`: ortak `LogRecord` semasi
- `tests/`: faz bazli testler
- `docs/`: kararlar, specs, faz state ve faz raporlari
- `output/`: role bazli cikti dosyalari
- `reports/`: metrics/stress raporlari

## Hizli Baslangic

Gereksinimler:

- Python 3.11+
- Docker + Docker Compose

Kurulum:

```bash
python -m pip install -r producer/requirements.txt
python -m pip install -r middleware/requirements.txt
python -m pip install pytest
```

Container'lari baslat:

```bash
docker compose up --build
```

## Producer Komutlari

Dry run:

```bash
python -m producer.src.main --dry-run --total 100 --batch 20 --rate 200
```

RabbitMQ'ya publish:

```bash
python -m producer.src.main --total 1000 --batch 100 --rate 500
```

Stress profil dosyasi uret:

```bash
python -m producer.src.stress.load_runner --profile ramp --reports-dir reports --max-total 50000
```

## Middleware Endpoints

- `GET /health`
- `GET /metrics`

Ornek:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## Cikti Dosyalari

Varsayilan role->format eslesmesi:

- `sysadmin -> output/sysadmin.md`
- `developer -> output/developer.json`
- `security -> output/security.csv`

Opsiyonel olarak HTML de desteklenir (konfig ile).

## Testler

Tum testleri calistir:

```bash
python -m pytest -q
```

E2E smoke (docker gerekir):

```bash
python scripts/e2e_smoke.py
```

Faz bazli:

```bash
python -m pytest -q tests/test_phase1_producer.py
python -m pytest -q tests/test_phase2_middleware.py
python -m pytest -q tests/test_phase3_pipeline.py
python -m pytest -q tests/test_phase4_formatting.py
python -m pytest -q tests/test_phase5_metrics_and_stress.py
```

## Dokumantasyon

- Mimari kararlar: `docs/DECISIONS.md`
- Davranis sozlesmesi: `docs/SPECS.md`
- Faz durumu: `docs/STATE.md`
- Faz raporlari: `docs/phase-reports/`

## CI/CD

GitHub Actions workflow:

- `.github/workflows/ci.yml`
  - `tests` job: dependency install + `pytest` + `docker compose config`
  - `e2e-smoke` job: `scripts/e2e_smoke.py` calistirir
  - `output/` ve `reports/` artifact olarak upload edilir

## Video / Teslim Icigi

Video anlatiminda su akisi takip edilebilir:

1. Sistem mimarisi (Producer -> RabbitMQ -> Middleware)
2. KVKK anonimlestirme canli ornegi
3. Filtreleme ve role bazli ciktilar
4. Stres profili ve metrics raporlari
5. Tasarim kaliplari (CoR, Strategy, Decorator, Factory, Singleton)
