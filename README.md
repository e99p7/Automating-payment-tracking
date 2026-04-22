
# Payment Tracking Production Project

Ready-made production is an option for an "Automating-payment-tracking" laptop, already with real files.

## What has been changed
- the input files have been renamed to:
- `data/input/arenda.xlsx `
- `data/input/print.xlsx `
- the parser `print.xlsx ` adapted to the real statement of the Savings Bank, where operations are carried out in blocks on pages, rather than a regular table
- The CLI and API use these names by default.

## Structure
```text
payment_tracking_prod_v2/
├─ api/main.py
├─ src/config.py
├─ src/excel_io.py
├─ src/payment_tracker.py
├─ src/schemas.py
├─ src/utils.py
├─ process_payments.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .env.example
├─ sample_request.json
├─ data/input/
│  ├─ arenda.xlsx
│  └─ print.xlsx
└─ data/output/
```

## Quick launch locally
```bash
pip install -r requirements.txt
python process_payments.py --today 2025-06-12
```

By default, they are used:
- `data/input/arenda.xlsx`
- `data/input/print.xlsx`
- result: `data/output/report.xlsx `

## Launching the API
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger:
- `http://localhost:8000/docs`

## REST by paths
```bash
curl -X POST "http://localhost:8000/process/path" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## REST with file upload
```bash
curl -X POST "http://localhost:8000/process/upload" \
  -F "arenda_file=@data/input/arenda.xlsx" \
  -F "bank_file=@data/input/print.xlsx" \
  -F "today=2025-06-12" \
  -F "grace_days=3"
```

## Docker
```bash
docker compose up --build
```

---

# Payment Tracking Production Project

Готовый production-вариант под ноутбук `Automating-payment-tracking`, уже с реальными файлами.

## Что изменено
- входные файлы переименованы в:
  - `data/input/arenda.xlsx`
  - `data/input/print.xlsx`
- парсер `print.xlsx` адаптирован под реальную выписку Сбера, где операции идут блоками по страницам, а не обычной таблицей
- CLI и API по умолчанию используют именно эти имена

## Структура
```text
payment_tracking_prod_v2/
├─ api/main.py
├─ src/config.py
├─ src/excel_io.py
├─ src/payment_tracker.py
├─ src/schemas.py
├─ src/utils.py
├─ process_payments.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .env.example
├─ sample_request.json
├─ data/input/
│  ├─ arenda.xlsx
│  └─ print.xlsx
└─ data/output/
```

## Быстрый запуск локально
```bash
pip install -r requirements.txt
python process_payments.py --today 2025-06-12
```

По умолчанию используются:
- `data/input/arenda.xlsx`
- `data/input/print.xlsx`
- результат: `data/output/report.xlsx`

## Запуск API
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger:
- `http://localhost:8000/docs`

## REST по путям
```bash
curl -X POST "http://localhost:8000/process/path" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## REST с загрузкой файлов
```bash
curl -X POST "http://localhost:8000/process/upload" \
  -F "arenda_file=@data/input/arenda.xlsx" \
  -F "bank_file=@data/input/print.xlsx" \
  -F "today=2025-06-12" \
  -F "grace_days=3"
```

## Docker
```bash
docker compose up --build
```
