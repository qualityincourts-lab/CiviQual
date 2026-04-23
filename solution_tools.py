"""
CiviQual Stats Solution Tools

Provides decision-making and solution evaluation tools:
- Pugh Matrix (Concept Selection)
- Impact/Effort Matrix

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import numpy as np


class PughScore(Enum):
    """Scoring options for Pugh Matrix."""
    MUCH_BETTER = 2
    BETTER = 1
    SAME = 0
    WORSE = -1
    MUCH_WORSE = -2


@dataclass
class PughCriterion:
    """A criterion in a Pugh Matrix."""
    name: str
    weight: float = 1.0
    description: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'weight': self.weight,
            'description': self.description
        }


@dataclass
class PughConcept:
    """A concept/alternative in a Pugh Matrix."""
    name: str
    description: str = ''
    is_baseline: bool = False
    scores: Dict[str, int] = field(default_factory=dict)  # criterion_name -> score
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'is_baseline': self.is_baseline,
            'scores': self.scores
        }


@dataclass
class PughMatrixResult:
    """Results of Pugh Matrix analysis."""
    concept: str
    weighted_score: float
    unweighted_score: float
    plus_count: int
    minus_count: int
    same_count: int
    rank: int
    
    def to_dict(self) -> Dict:
        return {
            'concept': self.concept,
            'weighted_score': self.weighted_score,
            'unweighted_score': self.unweighted_score,
            'plus_count': self.plus_count,
            'minus_count': self.minus_count,
            'same_count': self.same_count,
            'rank': self.rank
        }


@dataclass
class PughMatrix:
    """Complete Pugh Matrix for concept selection."""
    title: str
    criteria: List[PughCriterion] = field(default_factory=list)
    concepts: List[PughConcept] = field(default_factory=list)
    baseline_name: str = ''
    created_date: str = ''
    modified_date: str = ''
    notes: str = ''
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
    
    def add_criterion(self, name: str, weight: float = 1.0, description: str = '') -> PughCriterion:
        """Add a selection criterion."""
        criterion = PughCriterion(name=name, weight=weight, description=description)
        self.criteria.append(criterion)
        self.modified_date = datetime.now().isoformat()
        return criterion
    
    def add_concept(self, name: str, description: str = '', is_baseline: bool = False) -> PughConcept:
        """Add a concept/alternative."""
        concept = PughConcept(name=name, description=description, is_baseline=is_baseline)
        if is_baseline:
            self.baseline_name = name
            # Set all existing concepts' scores for this baseline
            for c in self.concepts:
                if c.is_baseline:
                    c.is_baseline = False
        self.concepts.append(concept)
        self.modified_date = datetime.now().isoformat()
        return concept
    
    def set_score(self, concept_name: str, criterion_name: str, score: int) -> None:
        """Set a score for a concept on a criterion."""
        for concept in self.concepts:
            if concept.name == concept_name:
                concept.scores[criterion_name] = score
                self.modified_date = datetime.now().isoformat()
                return
        raise ValueError(f"Concept '{concept_name}' not found")
    
    def calculate_results(self) -> List[PughMatrixResult]:
        """Calculate Pugh Matrix results for all concepts."""
        results = []
        
        for concept in self.concepts:
            if concept.is_baseline:
                # Baseline gets zero scores
                results.append(PughMatrixResult(
                    concept=concept.name,
                    weighted_score=0.0,
                    unweighted_score=0.0,
                    plus_count=0,
                    minus_count=0,
                    same_count=len(self.criteria),
                    rank=0
                ))
                continue
            
            weighted_score = 0.0
            unweighted_score = 0.0
            plus_count = 0
            minus_count = 0
            same_count = 0
            
            for criterion in self.criteria:
                score = concept.scores.get(criterion.name, 0)
                weighted_score += score * criterion.weight
                unweighted_score += score
                
                if score > 0:
                    plus_count += 1
                elif score < 0:
                    minus_count += 1
                else:
                    same_count += 1
            
            results.append(PughMatrixResult(
                concept=concept.name,
                weighted_score=weighted_score,
                unweighted_score=unweighted_score,
                plus_count=plus_count,
                minus_count=minus_count,
                same_count=same_count,
                rank=0  # Set after sorting
            ))
        
        # Sort by weighted score and assign ranks
        results.sort(key=lambda x: x.weighted_score, reverse=True)
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'criteria': [c.to_dict() for c in self.criteria],
            'concepts': [c.to_dict() for c in self.concepts],
            'baseline_name': self.baseline_name,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'notes': self.notes
        }
    
    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PughMatrix':
        """Import from JSON."""
        data = json.loads(json_str)
        matrix = cls(
            title=data['title'],
            baseline_name=data.get('baseline_name', ''),
            created_date=data.get('created_date', ''),
            notes=data.get('notes', '')
        )
        matrix.criteria = [PughCriterion(**c) for c in data.get('criteria', [])]
        for c_data in data.get('concepts', []):
            concept = PughConcept(
                name=c_data['name'],
                description=c_data.get('description', ''),
                is_baseline=c_data.get('is_baseline', False),
                scores=c_data.get('scores', {})
            )
            matrix.concepts.append(concept)
        return matrix
    
    def generate_text_report(self) -> str:
        """Generate a text report of the Pugh Matrix."""
        lines = []
        lines.append("=" * 70)
        lines.append(f"PUGH MATRIX: {self.title}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Baseline: {self.baseline_name}")
        lines.append(f"Criteria: {len(self.criteria)}")
        lines.append(f"Concepts: {len(self.concepts)}")
        lines.append("")
        
        # Header row
        header = f"{'Criterion':<25} {'Wt':>4}"
        for concept in self.concepts:
            header += f" {concept.name[:8]:>8}"
        lines.append(header)
        lines.append("-" * len(header))
        
        # Criterion rows
        for criterion in self.criteria:
            row = f"{criterion.name[:25]:<25} {criterion.weight:>4.1f}"
            for concept in self.concepts:
                if concept.is_baseline:
                    row += f" {'BASE':>8}"
                else:
                    score = concept.scores.get(criterion.name, 0)
                    score_str = f"{score:+d}" if score != 0 else "0"
                    row += f" {score_str:>8}"
            lines.append(row)
        
        lines.append("-" * len(header))
        
        # Results
        results = self.calculate_results()
        
        lines.append("")
        lines.append("RESULTS:")
        lines.append(f"{'Concept':<15} {'Weighted':>10} {'Rank':>6} {'+':>4} {'-':>4} {'S':>4}")
        lines.append("-" * 50)
        
        for result in results:
            lines.append(
                f"{result.concept[:15]:<15} {result.weighted_score:>10.1f} "
                f"{result.rank:>6} {result.plus_count:>4} {result.minus_count:>4} {result.same_count:>4}"
            )
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


@dataclass
class MatrixItem:
    """An item in an Impact/Effort Matrix."""
    name: str
    impact: float  # 1-10 scale
    effort: float  # 1-10 scale
    description: str = ''
    quadrant: str = ''  # Set after calculation
    priority_score: float = 0.0  # Set after calculation
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'impact': self.impact,
            'effort': self.effort,
            'description': self.description,
            'quadrant': self.quadrant,
            'priority_score': self.priority_score
        }


@dataclass
class ImpactEffortMatrix:
    """Impact/Effort Matrix for prioritization."""
    title: str
    items: List[MatrixItem] = field(default_factory=list)
    impact_threshold: float = 5.0  # Threshold between low/high
    effort_threshold: float = 5.0
    created_date: str = ''
    modified_date: str = ''
    notes: str = ''
    
    # Quadrant definitions
    QUICK_WINS = "Quick Wins"      # High Impact, Low Effort
    MAJOR_PROJECTS = "Major Projects"  # High Impact, High Effort
    FILL_INS = "Fill-Ins"          # Low Impact, Low Effort
    THANKLESS_TASKS = "Thankless Tasks"  # Low Impact, High Effort
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
    
    def add_item(self, name: str, impact: float, effort: float, description: str = '') -> MatrixItem:
        """Add an item to the matrix."""
        if not 1 <= impact <= 10:
            raise ValueError("Impact must be between 1 and 10")
        if not 1 <= effort <= 10:
            raise ValueError("Effort must be between 1 and 10")
        
        item = MatrixItem(name=name, impact=impact, effort=effort, description=description)
        self._assign_quadrant(item)
        self.items.append(item)
        self.modified_date = datetime.now().isoformat()
        return item
    
    def _assign_quadrant(self, item: MatrixItem) -> None:
        """Assign quadrant and priority score to an item."""
        high_impact = item.impact >= self.impact_threshold
        high_effort = item.effort >= self.effort_threshold
        
        if high_impact and not high_effort:
            item.quadrant = self.QUICK_WINS
            item.priority_score = item.impact / item.effort  # Higher is better
        elif high_impact and high_effort:
            item.quadrant = self.MAJOR_PROJECTS
            item.priority_score = item.impact / item.effort
        elif not high_impact and not high_effort:
            item.quadrant = self.FILL_INS
            item.priority_score = item.impact / item.effort
        else:
            item.quadrant = self.THANKLESS_TASKS
            item.priority_score = item.impact / item.effort
    
    def recalculate_quadrants(self) -> None:
        """Recalculate quadrants for all items (after threshold change)."""
        for item in self.items:
            self._assign_quadrant(item)
        self.modified_date = datetime.now().isoformat()
    
    def get_by_quadrant(self, quadrant: str) -> List[MatrixItem]:
        """Get all items in a specific quadrant."""
        return [item for item in self.items if item.quadrant == quadrant]
    
    def get_prioritized_list(self) -> List[MatrixItem]:
        """Get items sorted by priority (Quick Wins first, then by score)."""
        # Define quadrant priority order
        quadrant_order = {
            self.QUICK_WINS: 1,
            self.MAJOR_PROJECTS: 2,
            self.FILL_INS: 3,
            self.THANKLESS_TASKS: 4
        }
        
        return sorted(
            self.items,
            key=lambda x: (quadrant_order.get(x.quadrant, 5), -x.priority_score)
        )
    
    def get_statistics(self) -> Dict:
        """Get summary statistics for the matrix."""
        if not self.items:
            return {}
        
        impacts = [item.impact for item in self.items]
        efforts = [item.effort for item in self.items]
        
        return {
            'total_items': len(self.items),
            'quick_wins': len(self.get_by_quadrant(self.QUICK_WINS)),
            'major_projects': len(self.get_by_quadrant(self.MAJOR_PROJECTS)),
            'fill_ins': len(self.get_by_quadrant(self.FILL_INS)),
            'thankless_tasks': len(self.get_by_quadrant(self.THANKLESS_TASKS)),
            'avg_impact': np.mean(impacts),
            'avg_effort': np.mean(efforts),
            'impact_threshold': self.impact_threshold,
            'effort_threshold': self.effort_threshold
        }
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'items': [item.to_dict() for item in self.items],
            'impact_threshold': self.impact_threshold,
            'effort_threshold': self.effort_threshold,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'notes': self.notes
        }
    
    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ImpactEffortMatrix':
        """Import from JSON."""
        data = json.loads(json_str)
        matrix = cls(
            title=data['title'],
            impact_threshold=data.get('impact_threshold', 5.0),
            effort_threshold=data.get('effort_threshold', 5.0),
            created_date=data.get('created_date', ''),
            notes=data.get('notes', '')
        )
        for item_data in data.get('items', []):
            item = MatrixItem(**item_data)
            matrix.items.append(item)
        return matrix
    
    def generate_text_report(self) -> str:
        """Generate a text report of the Impact/Effort Matrix."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"IMPACT/EFFORT MATRIX: {self.title}")
        lines.append("=" * 60)
        lines.append("")
        
        stats = self.get_statistics()
        lines.append(f"Total Items: {stats.get('total_items', 0)}")
        lines.append(f"Thresholds: Impact >= {self.impact_threshold}, Effort >= {self.effort_threshold}")
        lines.append("")
        
        # Quick Wins
        lines.append("-" * 60)
        lines.append("QUICK WINS (High Impact, Low Effort) - Do First!")
        lines.append("-" * 60)
        for item in self.get_by_quadrant(self.QUICK_WINS):
            lines.append(f"  • {item.name}")
            lines.append(f"    Impact: {item.impact:.1f}  Effort: {item.effort:.1f}  Score: {item.priority_score:.2f}")
        if not self.get_by_quadrant(self.QUICK_WINS):
            lines.append("  (none)")
        lines.append("")
        
        # Major Projects
        lines.append("-" * 60)
        lines.append("MAJOR PROJECTS (High Impact, High Effort) - Plan Carefully")
        lines.append("-" * 60)
        for item in self.get_by_quadrant(self.MAJOR_PROJECTS):
            lines.append(f"  • {item.name}")
            lines.append(f"    Impact: {item.impact:.1f}  Effort: {item.effort:.1f}  Score: {item.priority_score:.2f}")
        if not self.get_by_quadrant(self.MAJOR_PROJECTS):
            lines.append("  (none)")
        lines.append("")
        
        # Fill-Ins
        lines.append("-" * 60)
        lines.append("FILL-INS (Low Impact, Low Effort) - Do If Time Permits")
        lines.append("-" * 60)
        for item in self.get_by_quadrant(self.FILL_INS):
            lines.append(f"  • {item.name}")
            lines.append(f"    Impact: {item.impact:.1f}  Effort: {item.effort:.1f}")
        if not self.get_by_quadrant(self.FILL_INS):
            lines.append("  (none)")
        lines.append("")
        
        # Thankless Tasks
        lines.append("-" * 60)
        lines.append("THANKLESS TASKS (Low Impact, High Effort) - Avoid or Delegate")
        lines.append("-" * 60)
        for item in self.get_by_quadrant(self.THANKLESS_TASKS):
            lines.append(f"  • {item.name}")
            lines.append(f"    Impact: {item.impact:.1f}  Effort: {item.effort:.1f}")
        if not self.get_by_quadrant(self.THANKLESS_TASKS):
            lines.append("  (none)")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_plot_data(self) -> Dict:
        """Get data formatted for plotting."""
        return {
            'items': [
                {
                    'name': item.name,
                    'x': item.effort,
                    'y': item.impact,
                    'quadrant': item.quadrant
                }
                for item in self.items
            ],
            'x_threshold': self.effort_threshold,
            'y_threshold': self.impact_threshold,
            'quadrant_labels': {
                'top_left': self.QUICK_WINS,
                'top_right': self.MAJOR_PROJECTS,
                'bottom_left': self.FILL_INS,
                'bottom_right': self.THANKLESS_TASKS
            }
        }
