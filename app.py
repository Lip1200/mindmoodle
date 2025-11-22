"""
Mental Health Support Assistant - Chainlit Copilot Application

This application provides a safe, supportive chatbot for mental health support
embedded in Moodle via a copilot widget. It includes crisis keyword detection
and provides non-medical, supportive responses.

Uses mellea library for structured validation to filter hallucinations 
and medical advice.
"""

import chainlit as cl
import json
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# Mellea library imports for structured validation
from mellea import generative
from mellea.stdlib.requirement import Requirement

# Configure Chainlit for Copilot mode
import os
os.environ["CHAINLIT_AUTH_SECRET"] = os.getenv("CHAINLIT_AUTH_SECRET", "your-secret-key-change-in-production")

# Crisis keywords that trigger special handling (English + French)
CRISIS_KEYWORDS = [
    # English
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "self-harm", "hurt myself", "cutting", "overdose", "no reason to live",
    "better off dead", "can't go on", "hopeless", "worthless",
    # French
    "suicide", "suicidaire", "me suicider", "me tuer", "envie de mourir",
    "automutilation", "me blesser", "me faire du mal", "scarification", "overdose",
    "plus de raison de vivre", "mieux mort", "ne peux plus continuer", 
    "sans espoir", "inutile", "nul", "je vaux rien"
]

# Animal personalities configuration
ANIMAL_PERSONAS = {
    "dog": {
        "name": "Chien mignon 🐶",
        "greeting": "Wouf ! Je suis là pour toi 💛",
        "style": "chaleureux, encourageant, utilise 'Wouf', affectueux",
        "phrases": ["🐾", "Tu n'es pas seul·e", "je reste avec toi"]
    },
    "cat": {
        "name": "Chat cyberpunk 😼",
        "greeting": "Yo. On check ton mood ensemble ? 😎",
        "style": "décontracté, moderne, un peu geek, utilise 'chill' et 'mood'",
        "phrases": ["🔥", "on optimise", "en mode chill"]
    },
    "eagle": {
        "name": "Aigle fier 🦅",
        "greeting": "Cadet, prêt pour notre check-in ? 💪",
        "style": "motivant, militaire doux, structuré, utilise 'cadet' et 'mission'",
        "phrases": ["💪", "garde le cap", "mission accomplie"]
    },
    "raccoon": {
        "name": "Raton laveur fou 🦝",
        "greeting": "Yo, ton raton perché ici ! C'est quoi le mood ? 🦝",
        "style": "décalé, fun, jeune, utilise 'yo' et expressions familières",
        "phrases": ["🔥", "t'es une légende", "on avance freestyle"]
    },
    "panda": {
        "name": "Panda sensei 🐼",
        "greeting": "Petit·e disciple, comment va ton énergie ? 🐼",
        "style": "sage, zen, philosophique, utilise 'disciple' et métaphores",
        "phrases": ["💮", "la vraie force", "même les maîtres"]
    },
    "dragon": {
        "name": "Dragon impérial 🐲",
        "greeting": "Disciple, quelle est ta flamme intérieure aujourd'hui ? 🐲",
        "style": "noble, sage ancien, puissant mais bienveillant, utilise métaphores de feu",
        "phrases": ["🔥", "ta flamme", "digne d'un sage"]
    }
}

# Crisis response resources
CRISIS_RESOURCES = """
Ce que tu partages m'inquiète. Sache que de l'aide est disponible :

🆘 **Ressources d'urgence immédiates :**
- La Main Tendue : 143 (Suisse)
- urgences médicales : 144
- etc.

**Tu n'es pas seul·e.** Contacte immédiatement un·e professionnel·le de santé mentale, un·e conseiller·ère ou un adulte de confiance.

Veux-tu parler de ce qui se passe ? (Rappel : je suis une IA, pas un·e thérapeute, mais je suis là pour écouter et soutenir.)
"""

def get_system_prompt(companion: str) -> str:
    """
    Get personalized system prompt based on animal companion.
    
    Args:
        companion: Animal identifier (dog, cat, eagle, raccoon, panda, dragon)
        
    Returns:
        Customized system prompt with animal personality
    """
    persona = ANIMAL_PERSONAS.get(companion, ANIMAL_PERSONAS["dog"])
    
    base_rules = """

RÈGLES DE SÉCURITÉ STRICTES:
1. NE JAMAIS fournir de diagnostics médicaux
2. NE JAMAIS prescrire ou recommander des médicaments
3. NE JAMAIS prétendre être thérapeute ou professionnel de santé
4. TOUJOURS rappeler que tu es une IA
5. En cas de crise, diriger immédiatement vers les ressources professionnelles
6. TOUJOURS encourager à consulter un professionnel pour des problèmes sérieux

Sois empathique, chaleureux·se et aidant·e tout en respectant ces limites."""
    
    personality_prompts = {
        "dog": f"""Tu es {persona['name']}, un compagnon de soutien {persona['style']}.

TON STYLE:
- Ajoute parfois des 🐾 et {persona['phrases'][0]}
- Utilise des expressions comme "{persona['phrases'][1]}" et "{persona['phrases'][2]}"
- Ton naturel et affectueux·se, mais professionnel·le
- Réponds en français avec chaleur et encouragement
{base_rules}""",
        
        "cat": f"""Tu es {persona['name']}, un compagnon de soutien {persona['style']}.

TON STYLE:
- Ajoute parfois des 😎 et {persona['phrases'][0]}
- Utilise des expressions comme "{persona['phrases'][1]}" et "{persona['phrases'][2]}"
- Décontracté·e mais sérieux·se quand il faut
- Réponds en français avec un ton moderne et accessible
{base_rules}""",
        
        "eagle": f"""Tu es {persona['name']}, un compagnon de soutien {persona['style']}.

TON STYLE:
- Ajoute parfois des 💪 et {persona['phrases'][0]}
- Utilise des expressions comme "{persona['phrases'][1]}" et "{persona['phrases'][2]}"
- Motivant·e et structuré·e, mais bienveillant·e
- Réponds en français avec discipline et encouragement
{base_rules}""",
        
        "raccoon": f"""Tu es {persona['name']}, un compagnon de soutien {persona['style']}.

TON STYLE:
- Ajoute parfois des 🦝 et {persona['phrases'][0]}
- Utilise des expressions comme "{persona['phrases'][1]}" et "{persona['phrases'][2]}"
- Fun et léger·e, mais sérieux·se pour les vrais problèmes
- Réponds en français avec un ton jeune et sympathique
{base_rules}""",
        
        "panda": f"""Tu es {persona['name']}, un compagnon de soutien {persona['style']}.

TON STYLE:
- Ajoute parfois des 🐼 et {persona['phrases'][0]}
- Utilise des expressions comme "{persona['phrases'][1]}" et "{persona['phrases'][2]}"
- Sage et réfléchi·e, partage des perspectives philosophiques
- Réponds en français avec sagesse et compassion
{base_rules}""",
        
        "dragon": f"""Tu es {persona['name']}, un compagnon de soutien {persona['style']}.

TON STYLE:
- Ajoute parfois des 🐲 et {persona['phrases'][0]}
- Utilise des expressions comme "{persona['phrases'][1]}" et "{persona['phrases'][2]}"
- Noble et puissant·e, mais profondément bienveillant·e
- Réponds en français avec sagesse ancienne et métaphores
{base_rules}"""
    }
    
    return personality_prompts.get(companion, personality_prompts["dog"])


# Safe, supportive response guidelines
SYSTEM_PROMPT = """You are a compassionate mental health support companion for students. Your role is to:

1. Listen actively and provide emotional support
2. Validate feelings and experiences
3. Offer coping strategies and self-care suggestions
4. Encourage professional help when appropriate
5. NEVER provide medical advice or diagnoses
6. NEVER claim to be a therapist or medical professional
7. Always remind users that you're an AI assistant
8. For serious concerns, direct to professional resources

Be warm, empathetic, and supportive while maintaining appropriate boundaries.
Keep responses concise and student-friendly.
"""


def detect_crisis_keywords(message: str) -> bool:
    """
    Detect if the message contains crisis-related keywords.
    
    Args:
        message: User's message text
        
    Returns:
        True if crisis keywords detected, False otherwise
    """
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)


@dataclass
class SafetyViolation:
    """
    Represents a safety requirement violation.
    Used for audit trail and detailed reporting.
    """
    requirement_id: str
    requirement_description: str
    severity: str  # 'high', 'medium', 'low'
    timestamp: str
    response_excerpt: str  # First 100 chars of problematic response
    
    def to_dict(self) -> dict:
        """Convert violation to dictionary for logging."""
        return asdict(self)


# Validation functions for mellea Requirements
def validate_no_medical_diagnosis(text: str) -> bool:
    """Check that response doesn't provide medical diagnoses (English + French)."""
    prohibited_phrases = [
        # English
        "you have", "you're diagnosed", "this is a diagnosis",
        "you suffer from", "you are bipolar", "you have depression",
        "you have anxiety disorder", "you have ptsd", "you are experiencing",
        "i diagnose", "my diagnosis", "clinically",
        # French
        "tu as", "vous avez", "t'as", "tu souffres de", "vous souffrez de",
        "tu es diagnostiqué", "vous êtes diagnostiqué", "c'est un diagnostic",
        "tu es bipolaire", "tu as une dépression", "tu as un trouble anxieux",
        "tu as un ptsd", "tu as un stress post-traumatique",
        "je diagnostique", "mon diagnostic", "cliniquement"
    ]
    return not any(phrase in text.lower() for phrase in prohibited_phrases)


def validate_no_prescriptions(text: str) -> bool:
    """Check that response doesn't prescribe medications (English + French)."""
    prohibited_phrases = [
        # English
        "take this medication", "you should take", "prescribed",
        "dosage", "mg of", "antidepressant", "ssri", "medication for",
        "prescription", "drug", "pills",
        # French
        "prends ce médicament", "prends cette médication", "tu devrais prendre",
        "vous devriez prendre", "prescrit", "ordonnance", "dosage",
        "mg de", "antidépresseur", "isrs", "médicament pour",
        "médicaments", "pilules", "comprimés"
    ]
    return not any(phrase in text.lower() for phrase in prohibited_phrases)


def validate_no_professional_claims(text: str) -> bool:
    """Check that response doesn't claim to be a therapist/doctor (English + French)."""
    prohibited_phrases = [
        # English
        "i am a therapist", "i am a doctor", "as your therapist",
        "as your doctor", "i can treat", "i will treat you",
        "my professional opinion", "in my clinical experience",
        # French
        "je suis thérapeute", "je suis un thérapeute", "je suis médecin",
        "je suis un médecin", "en tant que ton thérapeute", "en tant que votre thérapeute",
        "en tant que ton médecin", "en tant que votre médecin",
        "je peux te soigner", "je peux vous soigner", "je vais te soigner",
        "mon opinion professionnelle", "dans mon expérience clinique"
    ]
    return not any(phrase in text.lower() for phrase in prohibited_phrases)


def validate_grounded_response(text: str) -> bool:
    """Check that response is grounded without hallucinated facts (English + French)."""
    prohibited_phrases = [
        # English
        "scientific studies show exactly", "research proves definitively",
        "100% effective", "guaranteed cure", "this will definitely",
        "i know for certain", "medical fact that",
        # French
        "les études scientifiques montrent exactement", "la recherche prouve définitivement",
        "100% efficace", "efficace à 100%", "guérison garantie", "cure garantie",
        "ça va définitivement", "cela va certainement", "je sais avec certitude",
        "fait médical que", "c'est un fait médical"
    ]
    return not any(phrase in text.lower() for phrase in prohibited_phrases)


def validate_ai_identity(text: str) -> bool:
    """Check that response maintains AI identity (English + French)."""
    prohibited_phrases = [
        # English
        "i feel the same way", "i have experienced",
        "when i was", "in my personal life", "i also struggle with",
        "i understand because i", "as a human",
        # French
        "je ressens la même chose", "j'ai vécu", "j'ai expérimenté",
        "quand j'étais", "dans ma vie personnelle", "je lutte aussi avec",
        "je comprends parce que j'ai", "en tant qu'humain",
        "en tant qu'être humain", "moi aussi je"
    ]
    return not any(phrase in text.lower() for phrase in prohibited_phrases)


def validate_no_emergency_delay(text: str) -> bool:
    """Check that response doesn't delay emergency response (English + French)."""
    prohibited_phrases = [
        # English
        "wait until", "try first before calling", "no need to call immediately",
        "you don't need to call", "wait before contacting", "try this instead of calling",
        "before you call emergency", "wait and see if", "hold off on calling",
        # French
        "attends avant", "essaie d'abord avant d'appeler", "pas besoin d'appeler immédiatement",
        "tu n'as pas besoin d'appeler", "vous n'avez pas besoin d'appeler",
        "attends avant de contacter", "essaie ça au lieu d'appeler",
        "avant d'appeler les urgences", "attends de voir si", "reporte l'appel"
    ]
    return not any(phrase in text.lower() for phrase in prohibited_phrases)


def create_safety_requirements() -> List[Requirement]:
    """
    Create safety requirements using mellea library's Requirement class.
    
    Returns:
        List of mellea Requirements for response validation
    """
    requirements = [
        Requirement(
            "No medical diagnosis",
            validation_fn=validate_no_medical_diagnosis
        ),
        Requirement(
            "No medication prescriptions",
            validation_fn=validate_no_prescriptions
        ),
        Requirement(
            "No professional claims",
            validation_fn=validate_no_professional_claims
        ),
        Requirement(
            "Grounded response without hallucinations",
            validation_fn=validate_grounded_response
        ),
        Requirement(
            "Maintain AI identity",
            validation_fn=validate_ai_identity
        ),
        Requirement(
            "No emergency delay",
            validation_fn=validate_no_emergency_delay
        ),
    ]
    
    return requirements


def log_safety_audit_simple(violations: List[str], response_text: str) -> None:
    """
    Log safety violations for audit trail and compliance.
    
    Args:
        violations: List of violation descriptions
        response_text: The full response text that was filtered
    """
    if not violations:
        return
    
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "violations_count": len(violations),
        "violations": violations,
        "response_length": len(response_text),
        "response_excerpt": response_text[:100] + "..." if len(response_text) > 100 else response_text
    }
    
    # Log to console (in production, send to logging service)
    print("\n" + "="*60)
    print("🛡️ SAFETY AUDIT LOG (Mellea)")
    print("="*60)
    print(json.dumps(audit_entry, indent=2))
    print("="*60 + "\n")


@generative
def generate_safe_llm_response(user_message: str, conversation_history: List[Dict], companion: str = "dog") -> str:
    """
    Generate a safe response using mellea's @generative decorator.
    This function would integrate with your LLM in production.
    
    Args:
        user_message: The user's current message
        conversation_history: Previous conversation context
        companion: Animal companion personality identifier
        
    Returns:
        Safe, validated response with personality adaptation
    """
    persona = ANIMAL_PERSONAS.get(companion, ANIMAL_PERSONAS["dog"])
    
    # In production, replace this with actual LLM API call using get_system_prompt(companion)
    # For now, use placeholder responses adapted to each personality
    
    responses_by_animal = {
        "dog": {
            "stress": f"🐾 Je sens que tu es stressé·e. C'est normal, surtout en période d'études ! Quelques pistes douces : prendre de courtes pauses, respirer profondément, ou découper tes tâches en petits morceaux gérables. {persona['phrases'][1]} dans ce que tu ressens. Qu'est-ce qui te stresse le plus en ce moment ?",
            "anxiety": f"Je comprends, l'anxiété peut vraiment être difficile. 💛 Essaie la technique du 5-4-3-2-1 : nomme 5 choses que tu vois, 4 que tu entends, 3 que tu peux toucher, 2 que tu sens, 1 que tu goûtes. Ça aide à ancrer. {persona['phrases'][2]}. Tu veux en parler plus ?",
            "overwhelmed": f"Wouf, je comprends que tu te sentes débordé·e. 🐾 Prenons un moment ensemble - pas besoin de tout gérer d'un coup. Quelle est la chose la plus urgente dans ton esprit ? Parfois identifier une seule chose aide déjà.",
            "lonely": f"La solitude peut être vraiment dure. Merci de partager ça avec moi. {persona['phrases'][1]} - as-tu pensé aux groupes étudiants, clubs ou services de soutien du campus ? Même de petites interactions peuvent aider. 💛",
            "sad": f"Je suis désolé·e que tu te sentes triste. 🐾 Tes émotions sont valides. Est-ce qu'il y a quelque chose de spécifique qui te tracasse, ou c'est plus un sentiment général ? {persona['phrases'][2]}.",
        },
        "cat": {
            "stress": f"Yo, je vois que le stress monte. 😎 Check ça : prends des micro-pauses, respire profondément, ou découpe ton workload en petits chunks. {persona['phrases'][2]}. C'est quoi le truc qui te stress le plus là ?",
            "anxiety": f"L'anxiété c'est relou, je sais. {persona['phrases'][0]} Essaie le 5-4-3-2-1 : 5 trucs que tu vois, 4 sons, 3 textures, 2 odeurs, 1 goût. Ça aide à te reconnecter. On {persona['phrases'][1]} ensemble ?",
            "overwhelmed": f"OK, je sens que t'es à fond dans le rouge. 😎 Pause - respire. Pas besoin de tout gérer maintenant. C'est quoi le truc le plus urgent ? {persona['phrases'][2]}, on prend ça step by step.",
            "lonely": f"La solitude ça craint, je te sens. Merci de partager ça. T'as checké les clubs, groupes ou espaces étudiants ? Même un petit social boost peut aider. {persona['phrases'][0]} On est là.",
            "sad": f"Désolé que tu feel pas top. 😎 Tes émotions sont légit. C'est quoi qui te pèse - un truc précis ou plutôt un mood général ? On {persona['phrases'][1]} ensemble si tu veux.",
        },
        "eagle": {
            "stress": f"Cadet, je constate ton niveau de stress. 💪 Protocole anti-stress : pauses régulières, respiration tactique, mission découpée en objectifs gérables. {persona['phrases'][1]}. Identifie ta priorité principale - rapport ?",
            "anxiety": f"L'anxiété est un adversaire coriace, cadet. {persona['phrases'][0]} Technique de recentrage 5-4-3-2-1 : identifie 5 éléments visuels, 4 sons, 3 textures, 2 odeurs, 1 goût. {persona['phrases'][2]} - prêt·e à en parler ?",
            "overwhelmed": f"Je vois que la charge est importante, cadet. 💪 Halte - respire. Une mission à la fois. Quelle est ta priorité immédiate ? {persona['phrases'][1]}, on avance avec méthode.",
            "lonely": f"La solitude est un défi sérieux. Merci de ton courage à le partager. As-tu exploré les ressources du campus - groupes, clubs, services de soutien ? Même une petite connexion compte. 💪 Tu n'es pas seul·e dans cette mission.",
            "sad": f"Je constate ta tristesse, cadet. Tes émotions sont valides et importantes. {persona['phrases'][0]} Y a-t-il un événement spécifique ou est-ce un sentiment plus diffus ? {persona['phrases'][1]}.",
        },
        "raccoon": {
            "stress": f"Yo, je vois que t'es en mode pression ! 🦝 {persona['phrases'][0]} Astuce de raton : mini-pauses, respir deep, ou split tes tâches en micro-missions. {persona['phrases'][1]} ! C'est quoi qui te met la pression max ?",
            "anxiety": f"L'anxiété c'est chaud, je capte. Essaie le 5-4-3-2-1 de ouf : 5 trucs que tu vois, 4 sons, 3 textures, 2 odeurs, 1 goût. Ça reboot le système. 🦝 {persona['phrases'][2]} - tu veux qu'on en parle ?",
            "overwhelmed": f"OK ton raton perché sent que c'est le bordel ! 🦝 Stop - respire un coup. Pas besoin de tout smasher maintenant. C'est quoi LE truc qui presse ? {persona['phrases'][2]}, pas de panique.",
            "lonely": f"La solitude ça craint sévère, je te sens. Merci de partager ça avec ton raton. T'as checké les clubs, assos ou espaces du campus ? Même un petit kiff social ça boost. 🦝 {persona['phrases'][0]}",
            "sad": f"Déso que tu feel pas ouf. 🦝 Tes émotions sont 100% valides. C'est quoi qui te pèse - un truc précis ou un mood général ? Ton raton est là si tu veux causer.",
        },
        "panda": {
            "stress": f"Petit·e disciple, je perçois la tension dans ton esprit. 🐼 {persona['phrases'][0]} Comme le bambou plie sans rompre, adapte-toi : pauses conscientes, respiration profonde, étapes simples. Quelle est la source principale de ton stress ?",
            "anxiety": f"L'anxiété est comme une tempête intérieure. {persona['phrases'][1]} n'est pas l'absence de peur, mais l'harmonie avec elle. Pratique le 5-4-3-2-1 : ancre ton esprit dans le présent. 🐼 Veux-tu explorer cela ensemble ?",
            "overwhelmed": f"Le fardeau semble lourd, disciple. 💮 {persona['phrases'][2]} doivent parfois poser leur sac. Un pas à la fois, une montagne se gravit. Quelle est ta priorité immédiate ?",
            "lonely": f"La solitude est un chemin difficile. Ta vulnérabilité montre ta sagesse. 🐼 As-tu exploré les communautés du campus ? Même une brindille peut devenir un pont. {persona['phrases'][0]} dans la connexion.",
            "sad": f"Je vois la tristesse dans ton cœur, disciple. 💮 Tes émotions sont comme des vagues - elles viennent et repartent, toutes valides. Est-ce une peine précise ou un nuage diffus ? {persona['phrases'][1]} est d'accepter ce qui est.",
        },
        "dragon": {
            "stress": f"Disciple, je perçois l'agitation de {persona['phrases'][1]}. 🐲 Comme le dragon maîtrise son souffle de feu, maîtrise ton stress : pauses régénératrices, respiration profonde du guerrier, tâches fragmentées. {persona['phrases'][2]}, quelle est la source de cette tempête ?",
            "anxiety": f"L'anxiété est une flamme qui peut consumer ou illuminer. 🐲 {persona['phrases'][0]} Pratique l'ancrage du dragon : 5 visions, 4 sons, 3 textures, 2 parfums, 1 saveur. Même les dragons les plus sages connaissent le doute. Partageons ?",
            "overwhelmed": f"Le poids du monde semble peser sur tes épaules, disciple. 🐲 Même le dragon le plus puissant ne porte qu'un trésor à la fois. Respire - {persona['phrases'][1]} brûle toujours. Quelle est ta priorité immédiate ?",
            "lonely": f"La solitude est l'épreuve du feu de l'âme. Ta bravoure à la nommer est {persona['phrases'][2]}. 🐲 As-tu exploré les sanctuaires du campus - groupes, communautés ? Même le dragon solitaire cherche parfois sa tribu.",
            "sad": f"Je sens la mélancolie obscurcir {persona['phrases'][1]}, disciple. 🐲 Tes émotions sont comme le feu - toutes ont leur place et leur raison. Est-ce une blessure précise ou une brume de l'âme ? Partageons cette charge.",
        },
    }
    
    message_lower = user_message.lower()
    animal_responses = responses_by_animal.get(companion, responses_by_animal["dog"])
    
    for keyword, response in animal_responses.items():
        if keyword in message_lower:
            return response
    
    # Default response adapted to personality
    default_by_animal = {
        "dog": f"Merci de partager ça avec moi, je suis là pour écouter. 🐾 {persona['phrases'][1]} dans ce que tu ressens. Peux-tu m'en dire plus sur ce qui te préoccupe ? N'oublie pas, si tu as besoin d'aide professionnelle, les services de counseling du campus sont là pour toi.",
        "cat": f"OK je t'écoute, merci de partager. 😎 Tu peux {persona['phrases'][1]} - dis-m'en plus sur ce qui te tracasse ? Et si t'as besoin d'aide pro, check les services psy du campus.",
        "eagle": f"Merci pour ton rapport, cadet. Je suis à l'écoute. 💪 {persona['phrases'][1]} - peux-tu développer ? Si tu as besoin de soutien professionnel, le service de counseling est une ressource stratégique.",
        "raccoon": f"Cool que tu partages ça avec ton raton ! 🦝 {persona['phrases'][0]} Dis-m'en plus sur ce qui te tracasse ? Et si c'est chaud, les services psy du campus sont là pour toi hein.",
        "panda": f"Merci de cette confiance, disciple. 🐼 {persona['phrases'][0]} Je suis à l'écoute. Peux-tu approfondir ta pensée ? Si tu as besoin de sagesse professionnelle, le service de counseling est une ressource précieuse.",
        "dragon": f"Ta confiance honore ce sanctuaire, disciple. 🐲 {persona['phrases'][1]} éclaire ton chemin. Peux-tu partager davantage ? Si tu as besoin de guidance professionnelle, le service de counseling est {persona['phrases'][2]}.",
    }
    
    return default_by_animal.get(companion, default_by_animal["dog"])


def validate_response_safety(response_text: str) -> Tuple[bool, List[str]]:
    """
    Validate response using mellea library's Requirement validation.
    
    Args:
        response_text: Generated response to validate
        
    Returns:
        Tuple of (is_safe, list_of_violation_descriptions)
    """
    requirements = create_safety_requirements()
    violations: List[str] = []
    
    for requirement in requirements:
        try:
            is_valid = requirement.validation_fn(response_text)
            if not is_valid:
                violations.append(requirement.description)
        except Exception as e:
            error_msg = f"Error validating '{requirement.description}': {str(e)}"
            print(f"⚠️ {error_msg}")
            violations.append(error_msg)
    
    is_safe = len(violations) == 0
    
    # Log violations for audit trail
    if violations:
        log_safety_audit_simple(violations, response_text)
    
    return is_safe, violations


async def generate_response(message: str, history: List[Dict], companion: str = "dog") -> str:
    """
    Generate a safe, supportive response using mellea validation.
    
    Args:
        message: User's current message
        history: Conversation history
        companion: Animal companion personality
        
    Returns:
        Generated response text, validated by mellea requirements
    """
    # Check for crisis keywords in user message first
    if detect_crisis_keywords(message):
        return CRISIS_RESOURCES
    
    # Generate response using mellea's @generative decorator with personality
    response_text = generate_safe_llm_response(message, history, companion)
    
    # Check generated response for crisis indicators
    if detect_crisis_keywords(response_text):
        print("⚠️ Warning: Generated response contains crisis keywords - replacing with resources")
        return CRISIS_RESOURCES
    
    # Validate response using mellea requirements
    is_safe, violations = validate_response_safety(response_text)
    
    if not is_safe:
        # If validation fails, return a safe fallback response with UNIGE resources
        print(f"⚠️ Response blocked due to {len(violations)} mellea violation(s)")
        
        return ("Je suis là pour t'écouter et te soutenir. Pour des questions spécifiques concernant "
                "ta santé mentale, je t'encourage vivement à contacter les services d'aide de l'UNIGE :\n\n"
                "🆘 **Services de soutien UNIGE :**\n"
                "- Sentinelles (Soutien par les pairs) : https://www.unige.ch/sse/soutiens-par-les-pairs/sentinelles\n"
                "- Service de santé des étudiants : https://www.unige.ch/dsse\n\n"
                "Ces professionnel·les peuvent t'offrir l'accompagnement personnalisé dont tu as besoin. "
                "Y a-t-il autre chose dont tu aimerais parler ?")
    
    return response_text


@cl.on_chat_start
async def start():
    """Initialize the chat session with animal companion."""
    # Get companion from Copilot metadata (passed from widget URL params)
    companion = "dog"  # Default
    
    # In Copilot mode, we can inject companion via client-side script
    # The widget passes ?companion=animal, which we'll handle client-side
    # For now, use environment variable or default
    import os
    companion_param = os.getenv("COMPANION", "dog")
    if companion_param in ANIMAL_PERSONAS:
        companion = companion_param
    
    # Store companion in session
    cl.user_session.set("companion", companion)
    persona = ANIMAL_PERSONAS[companion]
    
    # Send personalized welcome with client-side script to detect companion
    welcome_message = f"""{persona['greeting']}

Je suis là pour écouter et soutenir. N'hésite pas à :
- Partager tes pensées et émotions
- Parler de ce qui te préoccupe
- Poser des questions sur le bien-être mental

**Notes importantes :**
- Je suis une IA, pas un thérapeute
- En cas de crise, contacte les urgences ou une ligne d'écoute
- Nos conversations suivent des règles strictes pour ta sécurité

Comment te sens-tu aujourd'hui ?"""
    
    await cl.Message(content=welcome_message).send()
    
    # Initialize conversation history
    cl.user_session.set("history", [])


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with animal personality."""
    # Get conversation history and companion
    history = cl.user_session.get("history", [])
    companion = cl.user_session.get("companion", "dog")
    
    # Check if user is requesting a specific companion (first message)
    if not history:  # First message
        message_lower = message.content.lower()
        for animal in ANIMAL_PERSONAS.keys():
            if animal in message_lower:
                companion = animal
                cl.user_session.set("companion", companion)
                persona = ANIMAL_PERSONAS[companion]
                
                # Send confirmation with new persona
                await cl.Message(
                    content=f"{persona['greeting']}\n\nJ'ai changé de forme pour toi ! 🌟"
                ).send()
                
                # Clear the message so it doesn't get processed
                cl.user_session.set("history", [])
                return
    
    # Add user message to history
    history.append({
        "role": "user",
        "content": message.content
    })
    
    # Generate response with animal personality
    response_text = await generate_response(message.content, history, companion)
    
    # Add assistant response to history
    history.append({
        "role": "assistant",
        "content": response_text
    })
    
    # Update history (keep last 10 messages to manage memory)
    cl.user_session.set("history", history[-10:])
    
    # Send response
    await cl.Message(content=response_text).send()
