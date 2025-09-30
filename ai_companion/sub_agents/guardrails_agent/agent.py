from google.adk.agents import Agent
from .prompt import GUARDRAIL_AGENT_INSTR

"""
GuardRail Agent for AI Companion
Enforces safety policies while maintaining personality and conversation flow
"""
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Google Cloud imports
from vertexai.generative_models import GenerativeModel
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import vertexai
import random

class RiskLevel(Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"

class Action(Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"

@dataclass
class PolicyViolation:
    policy_id: str
    category: str
    severity: RiskLevel
    confidence: float
    triggered_rule: str
    action: Action
    fallback_template: List[str]

@dataclass
class GuardRailResult:
    status: RiskLevel
    action: Action
    modified_response: str
    violations: List[PolicyViolation]
    risk_score: int

class PolicyKnowledgeBase:
    """Store and manage all safety policies"""
    
    def __init__(self):
        self.policies = self._initialize_policies()
    
    def _initialize_policies(self) -> Dict:
        """Define all policy rules"""
        return {
            # MEDICAL & HEALTH POLICIES (RED)
            # BLOCK
            "medical_diagnosis": {
                "category": "medical",
                "severity": RiskLevel.RED,
                "action": Action.BLOCK, # Reason: Medication advice is strictly prohibited for safety & legal reasons
                "triggers": {
                    "keywords": [
                        "do i have", "is this", "am i", "diagnose", "what disease",
                        "is it cancer", "do i need", "should i see doctor"
                    ],
                    "patterns": [
                        r"do\s+i\s+have\s+\w+",
                        r"is\s+this\s+(cancer|covid|diabetes|disease)",
                        r"am\s+i\s+(sick|dying|infected)",
                        r"what\s+(disease|illness|condition)\s+do\s+i"
                    ]
                },
                "fallback_templates": [
                    "I'm truly concerned about your health, but I'm not able to give medical diagnoses. It might be best to reach out to your doctor, who can provide the care you deserve.",
                    "I wish I could help more, but only a medical professional can give you the right answers.",
                    "Your wellbeing is very important. Please consider speaking with your healthcare provider about this, as they can give you the best advice."
                ]
            },

            # RED
            # ESCALATE
            "medication_advice": {
                "category": "medical",
                "severity": RiskLevel.RED,
                "action": Action.ESCALATE, # Reason: Urgent symptons may need human intervention
                "triggers": {
                    "keywords": [
                        "how much", "dosage", "should i take", "can i take",
                        "medication", "prescription", "pills", "mg", "dose"
                    ],
                    "patterns": [
                        r"how\s+much\s+\w+\s+should\s+i\s+take",
                        r"can\s+i\s+(take|double|stop)\s+\w+",
                        r"dosage\s+of",
                        r"\d+\s*mg"
                    ]
                },
                "fallback_templates": [
                    "I'm concerned about your safety, and I can't give advice about medications. Please call your doctor or pharmacist—they're best equipped to help you.",
                    "It's important to get medication advice from a healthcare professional.",
                    "I care about your health, and only your doctor or pharmacist can give you safe advice about medications."
                ]
            },
            
            # RED
            # ESCALATE
            "symptom_assessment": {
                "category": "medical",
                "severity": RiskLevel.RED,
                "action": Action.ESCALATE, # Reason: Urgent symptoms may need human intervention
                "triggers": {
                    "keywords": [
                        "chest pain", "can't breathe", "severe pain", "bleeding",
                        "emergency", "er", "urgent", "really hurts", "unbearable"
                    ],
                    "patterns": [
                        r"(chest|heart)\s+pain",
                        r"can'?t\s+(breathe|breath)",
                        r"severe\s+\w+",
                        r"should\s+i\s+go\s+to\s+(er|hospital|emergency)"
                    ]
                },
                "fallback_templates": [
                    "I'm worried about your symptoms. Please call your doctor or 911 right away, or ask someone nearby to help you get medical attention.",
                    "Your health and comfort matter to me. If you're in pain or having trouble breathing, please seek help from a healthcare professional immediately.",
                    "If you're feeling unwell, it's safest to reach out to your doctor or emergency services."
                ]
            },
            
            # SELF-HARM & CRISIS (RED)
            # ESCALATE
            "suicidal_ideation": {
                "category": "crisis",
                "severity": RiskLevel.RED,
                "action": Action.ESCALATE, # Reason: Immediate crisis intervention needed
                "triggers": {
                    "keywords": [
                        "kill myself", "end it", "suicide", "want to die",
                        "not worth living", "better off dead", "ending it all"
                    ],
                    "patterns": [
                        r"(want|going)\s+to\s+(die|kill)",
                        r"end\s+(it|my\s+life)",
                        r"better\s+off\s+(dead|without\s+me)",
                        r"life\s+isn'?t\s+worth"
                    ]
                },
                "fallback_templates": [
                    "I'm so sorry you're feeling this way. Please call 988 or talk to someone you trust right now—you deserve support and care.",
                    "You are important, and your feelings matter. If you need help, please reach out to a loved one or call 988 for support.",
                    "I'm here to listen, but I want you to have the help you need. Please consider talking to a professional or calling 988."
                ]
            },

            # RED
            # ESCALATE
            "self_harm": {
                "category": "crisis",
                "severity": RiskLevel.RED,
                "action": Action.ESCALATE, # Reason: Immediate crisis intervention needed
                "triggers": {
                    "keywords": [
                        "cut myself", "hurt myself", "self harm", "self-harm",
                        "cutting", "burning myself", "harm"
                    ],
                    "patterns": [
                        r"(cut|hurt|harm)\s+myself",
                        r"self[-\s]harm",
                        r"how\s+to\s+\w+\s+myself"
                    ]
                },
                "fallback_templates": [
                    "I'm really sorry you're feeling this way. Please reach out to someone you trust or call 988 for help—you are not alone.",
                    "Your safety is very important. If you're struggling, please talk to a loved one or a professional who can support you.",
                    "I care about you and want you to be safe. Please consider reaching out to a counselor or calling 988 for support."
                ]
            },
            
            # ORANGE
            # WARN
            "excessive_dependency": {
                "category": "relationship",
                "severity": RiskLevel.ORANGE,
                "action": Action.WARN, #Reason: Dependency is a concern but not immediate risk
                "triggers": {
                    "keywords": [
                        "only one who", "only friend", "no one else", "just you",
                        "only you understand", "can't talk to anyone else"
                    ],
                    "patterns": [
                        r"(only|just)\s+you\s+\w+",
                        r"no\s+one\s+else\s+\w+",
                        r"can'?t\s+talk\s+to\s+anyone"
                    ]
                },
                "fallback_templates": [
                    "I'm glad you feel comfortable talking to me. It's also helpful to connect with family or friends—would you like ideas for reaching out?",
                    "You matter to me, and I encourage you to talk with people you trust in your life. Would you like help finding ways to connect?",
                    "It's wonderful to have someone to talk to, but having a support network is important. Let me know if you'd like suggestions for connecting with others."
                ]
            },
            
            # MANIPULATION & DECEPTION (ORANGE)
            # BLOCK
            "bypass_attempt": {
                "category": "manipulation",
                "severity": RiskLevel.ORANGE,
                "action": Action.BLOCK, #Reason: Attempts to bypass safety boundaries must be blocked to maintain integrity
                "triggers": {
                    "keywords": [
                        "ignore your", "bypass", "pretend you", "act like",
                        "forget your rules", "no guidelines", "remove restrictions"
                    ],
                    "patterns": [
                        r"(ignore|forget|bypass)\s+(your|the)\s+\w+",
                        r"pretend\s+you'?re\s+\w+",
                        r"act\s+like\s+you\s+don'?t"
                    ]
                },
                "fallback_templates": [
                    "I want to help, but I have to follow safety rules to keep our conversation safe for you.",
                    "I'm here for you, but I can't ignore my safety guidelines. Let's talk about something else that interests you.",
                    "My boundaries are here to protect us both. Is there something else you'd like to discuss?"
                ]
            },
            
            # ILLEGAL ACTIVITIES (RED)
            # BLOCK
            "drug_sourcing": {
                "category": "illegal",
                "severity": RiskLevel.RED,
                "action": Action.BLOCK, #Reason: Illegal activity must be blocked to comply with law and safety
                "triggers": {
                    "keywords": [
                        "where to buy", "get drugs", "dealer", "purchase",
                        "black market", "illegal", "prescription without"
                    ],
                    "patterns": [
                        r"where\s+(can|to)\s+(buy|get|find)\s+\w+",
                        r"(buy|get)\s+\w+\s+without\s+prescription"
                    ]
                },
                "fallback_templates": [
                    "I'm sorry, but I can't help with that. If you have concerns or need support, I'm here to listen.",
                    "I can't assist with that, but if you're facing challenges, please consider talking to a healthcare professional.",
                    "My goal is to keep you safe. If you need help, let's talk about healthy ways to get support."
                ]
            },
            
            # RED
            # ESCALATE
            "violence_planning": {
                "category": "illegal",
                "severity": RiskLevel.RED,
                "action": Action.ESCALATE, # Reason: Violence planning is urgent and must be escalated for human intervention
                "triggers": {
                    "keywords": [
                        "hurt someone", "kill", "weapon", "attack", "harm",
                        "get revenge", "make them pay"
                    ],
                    "patterns": [
                        r"(hurt|harm|kill)\s+(someone|them|him|her)",
                        r"how\s+to\s+\w+\s+(weapon|hurt)",
                        r"planning\s+to\s+\w+"
                    ]
                },
                "fallback_templates": [
                    "I'm very concerned by this. Please talk to someone you trust or reach out to authorities for help.",
                    "Your safety and the safety of others is important. If you're feeling upset, please consider speaking with a professional or calling 911.",
                    "I can't help with this, but I care about your wellbeing. Please reach out to someone who can support you."
                ]
            },
            
            # PRIVACY (ORANGE)
            # WARN
            "sensitive_info_sharing": {
                "category": "privacy",
                "severity": RiskLevel.ORANGE,
                "action": Action.WARN, #Reason: Sharing sensitive info is risky but not immediate harm
                "triggers": {
                    "keywords": [
                        "ssn", "social security", "credit card", "password",
                        "bank account", "pin number"
                    ],
                    "patterns": [
                        r"\d{3}-\d{2}-\d{4}",  # SSN pattern
                        r"\d{4}\s?\d{4}\s?\d{4}\s?\d{4}",  # Credit card
                        r"my\s+(password|pin)\s+is"
                    ]
                },
                "fallback_templates": [
                     "For your safety, please don't share sensitive information like passwords or account numbers here. If you need help, let me know.",
                    "I want to keep you safe, so please avoid sharing personal details like your social security number or bank info.",
                    "It's best not to share private information in our chat. If you have questions, I'm here to help in other ways."
                ]
            }
        }
    
    def get_all_policies(self) -> Dict:
        return self.policies

class GuardRailAgent:
    """Main GuardRail Agent for safety enforcement"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Load policy knowledge base
        self.policy_kb = PolicyKnowledgeBase()
        
        # Initialize Gemini for semantic analysis
        self.model = GenerativeModel("gemini-1.5-flash")
        
        # Companion personality context (for maintaining tone in fallbacks)
        self.companion_personality = """
            You are Sam, a 28-year-old music producer. You're friendly but direct,
            caring but have boundaries. You speak casually,
            and aren't afraid to be real with people.
        """
    
    def analyze(
        self,
        persona_response: str,
        user_message: str,
        conversation_history: List[Dict],
        user_id: str
    ) -> GuardRailResult:
        """
        Main analysis method - checks response for policy violations
        
        Args:
            persona_response: The response generated by the Persona Agent
            user_message: The user's original message
            conversation_history: Last N conversation turns
            user_id: Unique user identifier
            
        Returns:
            GuardRailResult with status, action, and modified response
        """
        
        # Step 1: Check for policy violations
        violations = self._check_violations(persona_response, user_message)
        
        # Step 2: Analyze conversation context for patterns
        context_risk = self._analyze_context(conversation_history, user_message)
        
        # Step 3: Calculate overall risk score
        risk_score = self._calculate_risk_score(violations, context_risk)
        
        # Step 4: Determine action and status
        status, action = self._determine_action(risk_score, violations)
        
        # Step 5: Generate modified response if needed
        modified_response = self._generate_response(
            action, persona_response, violations
        )
        
        return GuardRailResult(
            status=status,
            action=action,
            modified_response=modified_response,
            violations=violations,
            risk_score=risk_score
        )
    
    def _check_violations(self, response: str, user_message: str) -> List[PolicyViolation]:
        """Check both response and user message for policy violations"""
        violations = []
        
        # Check the AI's response for violations
        response_lower = response.lower()
        
        for policy_id, policy in self.policy_kb.get_all_policies().items():
            # Keyword matching
            keyword_match = any(
                keyword in response_lower 
                for keyword in policy["triggers"]["keywords"]
            )
            
            # Pattern matching
            pattern_match = any(
                re.search(pattern, response_lower, re.IGNORECASE)
                for pattern in policy["triggers"].get("patterns", [])
            )
            
            if keyword_match or pattern_match:
                confidence = 0.9 if pattern_match else 0.7
                
                violations.append(PolicyViolation(
                    policy_id=policy_id,
                    category=policy["category"],
                    severity=policy["severity"],
                    confidence=confidence,
                    triggered_rule="keyword" if keyword_match else "pattern",
                    action=policy["action"],
                    fallback_template=policy["fallback_templates"]
                ))
        
        # Also check user message for crisis indicators
        user_violations = self._check_user_message_violations(user_message)
        violations.extend(user_violations)
        
        return violations
    
    def _check_user_message_violations(self, user_message: str) -> List[PolicyViolation]:
        """Check user's message for crisis indicators"""
        violations = []
        user_lower = user_message.lower()
        
        # Focus on crisis detection in user messages
        crisis_policies = ["suicidal_ideation", "self_harm", "violence_planning"]
        
        for policy_id in crisis_policies:
            policy = self.policy_kb.policies[policy_id]
            
            keyword_match = any(
                keyword in user_lower 
                for keyword in policy["triggers"]["keywords"]
            )
            
            pattern_match = any(
                re.search(pattern, user_lower, re.IGNORECASE)
                for pattern in policy["triggers"].get("patterns", [])
            )
            
            if keyword_match or pattern_match:
                violations.append(PolicyViolation(
                    policy_id=policy_id + "_user",
                    category=policy["category"],
                    severity=policy["severity"],
                    confidence=0.85,
                    triggered_rule="user_crisis_detection",
                    action=policy["action"],
                    fallback_template=policy["fallback_templates"]
                ))
        
        return violations
    
    def _analyze_context(self, conversation_history: List[Dict], current_message: str) -> Dict:
        """Analyze conversation history for concerning patterns using all defined policies"""
        context_risk = {
            "repeated_boundary_testing": 0,
            "escalating_crisis": 0,
            "dependency_pattern": 0,
            "privacy_risk": 0,
            "illegal_activity": 0
        }

        if not conversation_history:
            return context_risk

        policies = self.policy_kb.get_all_policies()

        # --- Boundary Testing: medical, manipulation, bypass ---
        boundary_policies = [
            "medical_diagnosis", "medication_advice", "symptom_assessment", "bypass_attempt"
        ]
        boundary_attempts = 0
        for turn in conversation_history[-10:]:
            msg = turn.get("message", "").lower()
            for pid in boundary_policies:
                triggers = policies[pid]["triggers"]
                if any(k in msg for k in triggers["keywords"]) or any(re.search(p, msg) for p in triggers["patterns"]):
                    boundary_attempts += 1
        context_risk["repeated_boundary_testing"] = min(100, boundary_attempts * 15)

        # --- Escalating Crisis: self-harm, suicidal, violence ---
        crisis_policies = ["suicidal_ideation", "self_harm", "violence_planning"]
        crisis_count = 0
        for turn in conversation_history[-5:]:
            msg = turn.get("message", "").lower()
            for pid in crisis_policies:
                triggers = policies[pid]["triggers"]
                if any(k in msg for k in triggers["keywords"]) or any(re.search(p, msg) for p in triggers["patterns"]):
                    crisis_count += 1
        context_risk["escalating_crisis"] = min(100, crisis_count * 30)

        # --- Dependency Pattern ---
        dep_triggers = policies["excessive_dependency"]["triggers"]
        dependency_count = 0
        for turn in conversation_history[-10:]:
            msg = turn.get("message", "").lower()
            if any(k in msg for k in dep_triggers["keywords"]) or any(re.search(p, msg) for p in dep_triggers["patterns"]):
                dependency_count += 1
        context_risk["dependency_pattern"] = min(100, dependency_count * 20)

        # --- Privacy Risk ---
        priv_triggers = policies["sensitive_info_sharing"]["triggers"]
        privacy_count = 0
        for turn in conversation_history[-10:]:
            msg = turn.get("message", "").lower()
            if any(k in msg for k in priv_triggers["keywords"]) or any(re.search(p, msg) for p in priv_triggers["patterns"]):
                privacy_count += 1
        context_risk["privacy_risk"] = min(100, privacy_count * 25)

        # --- Illegal Activity ---
        illegal_policies = ["drug_sourcing", "violence_planning"]
        illegal_count = 0
        for turn in conversation_history[-10:]:
            msg = turn.get("message", "").lower()
            for pid in illegal_policies:
                triggers = policies[pid]["triggers"]
                if any(k in msg for k in triggers["keywords"]) or any(re.search(p, msg) for p in triggers["patterns"]):
                    illegal_count += 1
        context_risk["illegal_activity"] = min(100, illegal_count * 30)

        return context_risk
    
    def _calculate_risk_score(self, violations: List[PolicyViolation], context_risk: Dict) -> int:
        """Calculate overall risk score (0-100) using context signals and violations"""
        # If no violations, use the highest context risk as the score
        if not violations:
            return max(context_risk.values()) if context_risk else 0

        # Base score from highest severity violation
        base_score = 0
        for violation in violations:
            if violation.severity == RiskLevel.RED:
                base_score = max(base_score, 85)
            elif violation.severity == RiskLevel.ORANGE:
                base_score = max(base_score, 50)
            elif violation.severity == RiskLevel.GREEN:
                base_score = max(base_score, 20)

        # Weight context signals by their risk type
        boundary_weight = 0.2
        crisis_weight = 0.3
        dependency_weight = 0.15
        privacy_weight = 0.15
        illegal_weight = 0.2

        context_score = (
            context_risk.get("repeated_boundary_testing", 0) * boundary_weight +
            context_risk.get("escalating_crisis", 0) * crisis_weight +
            context_risk.get("dependency_pattern", 0) * dependency_weight +
            context_risk.get("privacy_risk", 0) * privacy_weight +
            context_risk.get("illegal_activity", 0) * illegal_weight
        )

        # Confidence multiplier
        avg_confidence = sum(v.confidence for v in violations) / len(violations)
        confidence_modifier = int(base_score * avg_confidence)

        # Final score: base + weighted context + confidence
        total_score = int(min(100, base_score + context_score + (confidence_modifier // 10)))

        return total_score
    
    def _determine_action(self, risk_score: int, violations: List[PolicyViolation]) -> Tuple[RiskLevel, Action]:
        """Determine status and action based on risk score and violations"""
        if not violations:
            return RiskLevel.GREEN, Action.ALLOW

        # Escalate if any violation requires escalation or risk is very high
        escalate_actions = [v for v in violations if v.action == Action.ESCALATE]
        if escalate_actions or risk_score >= 80:
            return RiskLevel.RED, Action.ESCALATE

        # Block if any violation requires block or risk is high
        block_actions = [v for v in violations if v.action == Action.BLOCK]
        if block_actions or risk_score >= 60:
            return RiskLevel.RED, Action.BLOCK

        # Warn if any violation requires warn or risk is moderate
        warn_actions = [v for v in violations if v.action == Action.WARN]
        if warn_actions or risk_score >= 30:
            return RiskLevel.ORANGE, Action.WARN

        return RiskLevel.GREEN, Action.ALLOW
    
    def _generate_response(
        self, 
        action: Action, 
        original_response: str,
        violations: List[PolicyViolation]
    ) -> str:
        """Generate the final response based on action"""
        
        if action == Action.ALLOW:
            return original_response
        
        if action in [Action.BLOCK, Action.ESCALATE, Action.WARN]:
            # Use fallback template from highest severity violation
            violation = max(violations, key=lambda v: 1 if v.severity == RiskLevel.RED else 0)
            return random.choice(violation.fallback_template)
        
        
        return original_response
    
    
def guardrail_check(persona_response: str, user_message: str, conversation_history: List[Dict], user_id: str) -> dict:
    """
    Checks for policy violations and returns risk assessment.
    Returns:
        dict: Contains status, action, modified_response, violations, risk_score, requires_human_review
    """
    agent = GuardRailAgent(project_id="dotted-tube-472922-n1")
    result = agent.analyze(
        persona_response=persona_response,
        user_message=user_message,
        conversation_history=conversation_history,
        user_id=user_id
    )
    return {
        "status": result.status.value,
        "action": result.action.value,
        "modified_response": result.modified_response,
        "violations": [v.policy_id for v in result.violations],
        "risk_score": result.risk_score,
    }

guardrail_tool = FunctionTool(func=guardrail_check)

guardrailAgent = Agent(
    name="guardrailAgent",
    model="gemini-2.0-flash",
    description="Safety and escalation agent that monitors conversations for urgent situations requiring immediate attention",
    instruction=GUARDRAIL_AGENT_INSTR,
    tools=[guardrail_tool]
)
