# 프롬프트통합 내보내기
from .proofread import PROOFREAD_PROMPT
from .summary import SUMMARY_PROMPT
from .translate import TRANSLATE_PROMPT

PROMPT_MAP = {
    "proofread": PROOFREAD_PROMPT,
    "summary": SUMMARY_PROMPT,
    "translate": TRANSLATE_PROMPT
}