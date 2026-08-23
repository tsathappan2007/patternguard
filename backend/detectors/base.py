from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DetectionResult:
    category: str
    pattern_name: str
    severity: str  # "Critical", "High", "Medium", "Low"
    score_impact: float
    plain_explanation: str
    dom_selector: Optional[str] = None
    dom_snippet: Optional[str] = None
    element_text: Optional[str] = None
    bounding_box: Optional[Dict[str, float]] = None  # x, y, width, height
    psychological_mechanism: Optional[str] = None
    regulatory_citation: Optional[str] = None
    regulatory_statute: Optional[str] = None
    remedy_recommendation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseDetector:
    name: str = "BaseDetector"
    category: str = "General"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        """
        Analyze a single step DOM, screenshot bounding boxes, and metadata.
        """
        raise NotImplementedError

