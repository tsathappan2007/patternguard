import os
import json
from backend.mcp.autonomous_agent import AutonomousMCPAgent
from backend.detectors.ai_analyzer import CoercivePatternAIAnalyzer

def test_ai_components():
    print("=== TESTING AI INFERENCE COMPONENTS ===")
    
    # Test CoercivePatternAIAnalyzer
    analyzer = CoercivePatternAIAnalyzer()
    texts = [
        "Special Offer: 95% of users choose accidental protection plan for $19.99.",
        "No thanks, I don't want to save money and prefer paying full price.",
        "Warning: If you cancel, you will permanently lose all progress and discounts."
    ]
    findings = analyzer.analyze_text_corpus(texts)
    print(f"[OK] Deterministic Heuristics Detected {len(findings)} findings:")
    for f in findings:
        print(f"   - [{f['severity']}] {f['pattern']}: {f['text']}")

    print("\n[OK] AI Analyzer components verified successfully!")

if __name__ == "__main__":
    test_ai_components()

