"""Voice Interpretation skill — handle transcribed speech input."""

from typing import Any, Dict

from src.agents.skills.translation import detect_language


def process_voice_transcription(
    text: str,
    confidence: float = 1.0,
) -> Dict[str, Any]:
    """Process transcribed voice input before sending to agent pipeline.

    Args:
        text: Transcribed text from Web Speech API.
        confidence: Recognition confidence (0-1).

    Returns:
        Processed input ready for the agent pipeline.
    """
    cleaned = text.strip()
    language = detect_language(cleaned)

    if confidence < 0.5:
        return {
            "text": cleaned,
            "language": language,
            "confidence": confidence,
            "needs_confirmation": True,
            "prompt": f'I heard: "{cleaned}". Is that correct? You can say it again or type it.',
        }

    return {
        "text": cleaned,
        "language": language,
        "confidence": confidence,
        "needs_confirmation": False,
        "prompt": None,
    }
