# 🔍 AI Data Flow Analyzer (PHP / MVC)

Инструмент для анализа потоков данных в PHP-приложениях (MVC), сочетающий статический анализ и LLM.

Позволяет:

* находить использование полей
* строить поток данных (FORM → CONTROLLER → MODEL → SAVE)
* выявлять проблемы (потеря данных, отсутствие сохранения)
* автоматически анализировать код через LLM

---

# 🚀 Возможности

### ✅ Статический анализ

* READ / WRITE / SAVE детекция
* условия (if), вызовы методов
* анализ request (`request->data`, `$_POST`, `$_GET`)

### ✅ Data Flow (поток данных)

Автоматически строит цепочку:

```
FORM → CONTROLLER → MODEL → SAVE
```

---

### ✅ Глобальный поиск

* поиск поля по всему проекту
* группировка: Controller / Model / View
* фильтрация и лимиты

---

### ✅ LLM-анализ

* объясняет поведение поля
* находит проблемы
* предлагает рефакторинг

---

### ✅ Lifecycle Engine

Определяет тип поля:

| Тип           | Описание           |
| ------------- | ------------------ |
| STORED_FIELD  | сохраняется        |
| DERIVED_FIELD | только вычисляется |
| UNUSED        | не используется    |

---

# 🧠 Архитектура

```
QUERY
  ↓
parse_query
  ↓
find_target
  ↓
load code
  ↓
field detection
  ↓
analyzer (flow + input)
  ↓
proof
  ↓
global search
  ↓
LLM
  ↓
lifecycle
```

---

# 📁 Структура проекта

```
assistant/
│
├── core/
│   ├── engine.py
│   ├── analyzer.py
│   ├── search.py
│   ├── index_store.py
│   ├── lifecycle_engine.py
│   ├── lifecycle.py
│   ├── field_classifier.py
│   ├── model.py
│   └── global_search.py
│
├── proof/
│   ├── tracer.py
│   └── global_tracer.py
│
├── utils/
│   └── utils.py
│
├── prompts/
│   └── flow.txt
│
├── index/
│   └── index.json
│
└── config.py
```

---

# ⚙️ Установка

## 1. Клонирование

```bash
git clone <repo>
cd assistant
```

---

## 2. Установка зависимостей

```bash
pip install requests
```

---

## 3. Установка Ollama

Установи Ollama:

https://ollama.com

---

## 4. Загрузка модели

Рекомендуемая модель:

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

---

## 5. Настройка config.py

```python
FAST_MODEL = "qwen2.5:7b-instruct-q4_K_M"
DEEP_MODEL = "qwen2.5:7b-instruct-q4_K_M"

FAST_TOKENS = 800
DEEP_TOKENS = 4000
```

---

# ▶️ Использование

## Базовый запуск

```bash
python3 ai.py "SicsController admin_get_csv"
```

---

## Пример вывода

```
FIELD: total

READ:
- Controller: line 120
- Model: line 45

WRITE:
- line 200: $data['total'] = ...

INPUT:
- request->data['total']

FLOW:
FORM → CONTROLLER → MODEL → SAVE

STATUS: STORED_FIELD
```

---

# 🔍 Как это работает

## 1. Парсинг запроса

Извлекается:

* Controller
* Action
* Field (если есть)

---

## 2. Поиск метода

Ищется:

```
Controller + Action
```

---

## 3. Авто-детект поля

Если поле не указано:

* request->data
* переменные `$var`
* ключи массивов `['field']`

---

## 4. Анализ кода

```
find_field_flow()
```

Определяет:

* READ
* WRITE
* SAVE
* CONDITIONS
* CALLS

---

## 5. Построение отчёта

```
build_proof()
```

---

## 6. Глобальный поиск

```
find_field()
search_field_in_project()
```

---

## 7. LLM анализ

Контекст:

```
proof + global + code
```

---

## 8. Lifecycle

```
build_lifecycle()
```

---

# 🧪 Примеры задач

## Найти где используется поле

```bash
python3 ai.py "total"
```

---

## Разобрать поток данных

```bash
python3 ai.py "OrdersController add total"
```

---

## Дебаг

```bash
python3 ai.py "почему не сохраняется total"
```

---

# ⚡ Производительность

| Компонент | Время     |
| --------- | --------- |
| анализ    | ~0.1–0.5s |
| LLM       | 30–180s   |

---

# 🧱 Ограничения

* PHP parsing основан на regex (не AST)
* точность зависит от качества кода
* LLM может ошибаться (используется только как reasoning слой)

---

# 🔥 Roadmap

### V11

* multi-field анализ
* улучшенный auto-detect

### V12

* построение графа зависимостей
* cross-model flow

### V13

* web UI
* визуализация потоков

---

# 🤝 Вклад

PR и идеи приветствуются.

---

# 📄 Лицензия

MIT

