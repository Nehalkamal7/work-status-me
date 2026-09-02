import os
import json
import logging
from typing import List, Dict, Any
from app.schemas import ChatExecutiveSummary, ActionItem
import litellm

logger = logging.getLogger(__name__)

# Silent litellm telemetry
litellm.telemetry = False

class AIService:
    @staticmethod
    def clean_chat_messages(messages: List[Dict[str, str]]) -> str:
        """Filter system notices, automated messages, and trivial greetings."""
        cleaned = []
        ignore_patterns = ["<Media omitted>", "deleted this message", "joined using this group's invite link"]
        
        for m in messages:
            sender = m.get("sender", "Unknown")
            text = m.get("message_text", "").strip()
            
            if not text or any(pattern in text for pattern in ignore_patterns):
                continue
            
            # Simple length check for single word greetings
            if text in ["تم", "شكرا", "تمام", "أهلا", "مرحبا", "ok", "thanks"]:
                continue
                
            cleaned.append(f"{sender}: {text}")
            
        return "\n".join(cleaned)

    @classmethod
    async def analyze_chat_transcript(cls, group_name: str, messages: List[Dict[str, str]]) -> ChatExecutiveSummary:
        cleaned_text = cls.clean_chat_messages(messages)
        if not cleaned_text:
            return ChatExecutiveSummary(
                summary=f"لا توجد رسائل كافية أو هامة للتحليل في مجموعة {group_name}.",
                action_items=[],
                blockers_and_risks=[],
                confidence_score=1.0
            )

        prompt = f"""أنت مساعد ذكاء اصطناعي خبير لمدير المشروعات (PM).
قم بتحليل محادثات واتساب التالية لمجموعة: "{group_name}".

المحادثات:
{cleaned_text}

المطلوب:
1. ملخص تنفيذي موجّز ومباشر (Executive Summary).
2. قائمة المهام والإجراءات المطلوبة (Action Items) محدد فيها المهمة، صاحب الخطوة/المسؤول (Owner)، ومستوى الأهمية (High, Normal, Low).
3. المخاطر والعوائق المحددة (Blockers and Risks).

أخرج النتيجة بصيغة JSON مطابقة للشكل التالي:
{{
  "summary": "...",
  "action_items": [
    {{"task": "...", "owner": "...", "urgency": "High|Normal|Low"}}
  ],
  "blockers_and_risks": ["..."],
  "confidence_score": 0.95
}}
"""

        # Try LiteLLM call if API Key is configured in environment (OPENAI_API_KEY, GEMINI_API_KEY, etc.)
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        
        if api_key:
            try:
                model_name = "gpt-3.5-turbo" if os.environ.get("OPENAI_API_KEY") else "gemini/gemini-1.5-flash"
                response = await litellm.acompletion(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                data = json.loads(content)
                
                action_items = [ActionItem(**item) for item in data.get("action_items", [])]
                return ChatExecutiveSummary(
                    summary=data.get("summary", ""),
                    action_items=action_items,
                    blockers_and_risks=data.get("blockers_and_risks", []),
                    confidence_score=float(data.get("confidence_score", 0.95))
                )
            except Exception as e:
                logger.error(f"LLM API call failed: {e}. Falling back to NLP rules engine.")

        # Fallback Deterministic Rules Engine (runs if no external LLM key is provided)
        return cls._rule_based_fallback(group_name, messages)

    @classmethod
    def _rule_based_fallback(cls, group_name: str, messages: List[Dict[str, str]]) -> ChatExecutiveSummary:
        action_items = []
        blockers = []
        summary_lines = []

        keywords_action = ["مطلوب", "يرجى", "متابعة", "إرسال", "تسليم", "تعديل", "تحديث", "please", "send", "review"]
        keywords_risk = ["تأخير", "متوقف", "اعتراض", "مشكلة", "عائق", "بانتظار", "delay", "issue", "block"]

        for m in messages:
            sender = m.get("sender", "عضو الفريق")
            text = m.get("message_text", "")
            
            # Check actions
            if any(kw in text.lower() for kw in keywords_action):
                action_items.append(ActionItem(
                    task=text[:120],
                    owner=sender,
                    urgency="High" if any(u in text for u in ["عاجل", "ضروري", "urgent"]) else "Normal"
                ))
            
            # Check risks
            if any(kw in text.lower() for kw in keywords_risk):
                blockers.append(f"ملاحظة من {sender}: {text[:120]}")

            if len(summary_lines) < 3 and len(text) > 15:
                summary_lines.append(f"• {sender}: {text[:80]}")

        exec_summary = f"تم استخراج أهم المحادثات والإجراءات لمجموعة {group_name}.\n" + "\n".join(summary_lines)
        if not summary_lines:
            exec_summary = f"المحادثات مستقرة في مجموعة {group_name} وتتم متابعة المستجدات."

        return ChatExecutiveSummary(
            summary=exec_summary,
            action_items=action_items[:5],
            blockers_and_risks=blockers[:5],
            confidence_score=0.90
        )
