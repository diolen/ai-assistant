STRUCT_FILE = "index/index.json"
PROJECT_ROOT = "./app"

# =========================
# LLM CONFIG (OPTIMIZED)
# =========================

# ОДНА модель для всего
FAST_MODEL = "qcwind/qwen2.5-7B-instruct-Q4_K_M:latest"
DEEP_MODEL = "qcwind/qwen2.5-7B-instruct-Q4_K_M:latest"

# =========================
# TOKENS (SAFE LIMITS)
# =========================

# быстрый режим
FAST_TOKENS = 600

# глубокий режим (НЕ 4000!)
DEEP_TOKENS = 1500

# =========================
# PROMPT
# =========================
DEFAULT_PROMPT = "assistant/prompts/flow.txt"

# =========================
# RETRY
# =========================
RETRY_ON_EMPTY = True
MAX_RETRIES = 1