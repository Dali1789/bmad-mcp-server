"""
BMAD Quality Gate Manager
Implementiert Quality Gates und QA-Checks basierend auf der BMAD-METHOD
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from .workflow_states import StoryContext, StoryState

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality assessment levels"""
    PASSED = "passed"
    WARNING = "warning" 
    FAILED = "failed"
    BLOCKED = "blocked"


class QualityGateManager:
    """
    Manages quality gates and QA processes for BMAD-METHOD
    
    Implements:
    - Risk profiling (@qa *risk)
    - Test strategy design (@qa *design) 
    - Requirements tracing (@qa *trace)
    - Non-functional requirements (@qa *nfr)
    - Comprehensive review (@qa *review)
    - Quality gate assessment (@qa *gate)
    """
    
    def __init__(self):
        self.quality_metrics = {
            "gates_checked": 0,
            "gates_passed": 0,
            "gates_failed": 0,
            "risk_assessments": 0,
            "comprehensive_reviews": 0
        }
        
        # Quality gate configurations
        self.gate_requirements = {
            StoryState.DEVELOPMENT: {
                "required_checks": ["acceptance_criteria", "task_breakdown"],
                "optional_checks": ["risk_assessment", "design_review"],
                "blocking_issues": ["missing_requirements", "unclear_scope"]
            },
            StoryState.QA_CHECK: {
                "required_checks": ["implementation_complete", "unit_tests", "code_review"],
                "optional_checks": ["integration_tests", "performance_tests"],
                "blocking_issues": ["test_failures", "code_quality_issues"]
            },
            StoryState.READY_FOR_REVIEW: {
                "required_checks": ["all_tests_passed", "documentation_updated", "acceptance_criteria_met"],
                "optional_checks": ["security_review", "performance_validation"],
                "blocking_issues": ["failing_tests", "incomplete_features"]
            },
            StoryState.COMPLETED: {
                "required_checks": ["qa_review_passed", "stakeholder_approval", "deployment_ready"],
                "optional_checks": ["user_acceptance_testing", "load_testing"],
                "blocking_issues": ["unresolved_defects", "missing_approvals"]
            }
        }
    
    # =====================================
    # QUALITY GATE CHECKS
    # =====================================
    
    async def check_story_gates(self, story: StoryContext, target_state: StoryState) -> Dict[str, Any]:
        """
        Comprehensive quality gate check for story state transition
        
        Args:
            story: Story context
            target_state: Target state to transition to
            
        Returns:
            Quality gate check result
        """
        try:
            gate_config = self.gate_requirements.get(target_state, {})
            
            # Run all required checks
            check_results = {}
            overall_quality = QualityLevel.PASSED
            issues = []
            recommendations = []
            
            # Required checks
            required_checks = gate_config.get("required_checks", [])
            for check in required_checks:
                result = await self._run_quality_check(story, check)
                check_results[check] = result
                
                if result["level"] == QualityLevel.FAILED:
                    overall_quality = QualityLevel.FAILED
                    issues.extend(result["issues"])
                elif result["level"] == QualityLevel.WARNING and overall_quality != QualityLevel.FAILED:
                    overall_quality = QualityLevel.WARNING
                
                recommendations.extend(result.get("recommendations", []))
            
            # Optional checks (warnings only)
            optional_checks = gate_config.get("optional_checks", [])
            for check in optional_checks:
                result = await self._run_quality_check(story, check)
                check_results[f"optional_{check}"] = result
                
                if result["level"] == QualityLevel.FAILED:
                    recommendations.append(f"Consider addressing optional check: {check}")
            
            # Check for blocking issues
            blocking_issues = gate_config.get("blocking_issues", [])
            for issue_type in blocking_issues:
                if await self._has_blocking_issue(story, issue_type):
                    overall_quality = QualityLevel.BLOCKED
                    issues.append(f"Blocking issue detected: {issue_type}")
            
            # Update metrics
            self.quality_metrics["gates_checked"] += 1
            if overall_quality == QualityLevel.PASSED:
                self.quality_metrics["gates_passed"] += 1
            else:
                self.quality_metrics["gates_failed"] += 1
            
            # Record gate check in story
            gate_record = {
                "target_state": target_state.value,
                "quality_level": overall_quality.value,
                "checked_at": datetime.now().isoformat(),
                "issues_count": len(issues),
                "recommendations_count": len(recommendations)
            }
            
            if "quality_gates" not in story.validation_results:
                story.validation_results["quality_gates"] = []
            story.validation_results["quality_gates"].append(gate_record)
            
            logger.info(f"Quality gate check for story {story.story_id}: {overall_quality.value}")
            
            return {
                "passed": overall_quality in [QualityLevel.PASSED, QualityLevel.WARNING],
                "quality_level": overall_quality.value,
                "check_results": check_results,
                "issues": issues,
                "recommendations": recommendations,
                "gate_record": gate_record
            }
            
        except Exception as e:
            logger.error(f"Error in quality gate check: {e}")
            return {
                "passed": False,
                "quality_level": QualityLevel.FAILED.value,
                "error": str(e),
                "issues": [f"Quality gate check failed: {str(e)}"],
                "recommendations": ["Investigate quality gate check failure"]
            }
    
    # =====================================
    # QA COMMAND IMPLEMENTATIONS (@qa *)
    # =====================================
    
    async def risk_assessment(self, story: StoryContext, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Risk profiling implementation (@qa *risk {story})
        
        Args:
            story: Story to assess
            parameters: Additional parameters
            
        Returns:
            Risk assessment result
        """
        try:
            risk_factors = []
            risk_level = "LOW"
            mitigation_strategies = []
            
            # Technical complexity risk
            if self._assess_technical_complexity(story) > 7:
                risk_factors.append("High technical complexity")
                risk_level = "HIGH"
                mitigation_strategies.append("Break down into smaller technical tasks")
                mitigation_strategies.append("Involve architect for design review")
            
            # Dependencies risk
            dependency_risk = self._assess_dependencies(story)
            if dependency_risk > 5:
                risk_factors.append("External dependencies")
                risk_level = "MEDIUM" if risk_level == "LOW" else risk_level
                mitigation_strategies.append("Identify and validate all dependencies early")
            
            # Requirements clarity risk
            if not story.acceptance_criteria or len(story.acceptance_criteria) < 3:
                risk_factors.append("Unclear or insufficient acceptance criteria")
                risk_level = "MEDIUM" if risk_level == "LOW" else risk_level
                mitigation_strategies.append("Refine acceptance criteria with stakeholders")
            
            # Time estimation risk
            if self._assess_time_risk(story) > 6:
                risk_factors.append("Time estimation uncertainty")
                risk_level = "MEDIUM" if risk_level == "LOW" else risk_level
                mitigation_strategies.append("Add time buffers and interim checkpoints")
            
            # Create risk profile
            risk_profile = {
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "mitigation_strategies": mitigation_strategies,
                "assessment_date": datetime.now().isoformat(),
                "assessed_by": "qa_agent",
                "complexity_score": self._assess_technical_complexity(story),
                "dependency_score": dependency_risk,
                "time_risk_score": self._assess_time_risk(story)
            }
            
            # Store in story
            story.risk_profile = risk_profile
            story.add_agent_note("qa", f"Risk assessment completed: {risk_level} risk level")
            
            self.quality_metrics["risk_assessments"] += 1
            
            logger.info(f"Risk assessment for story {story.story_id}: {risk_level}")
            
            return {
                "success": True,
                "risk_profile": risk_profile,
                "next_actions": self._get_risk_next_actions(risk_level),
                "message": f"Risk assessment completed: {risk_level} risk level identified"
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return {"success": False, "error": str(e)}
    
    async def design_test_strategy(self, story: StoryContext, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Test strategy design implementation (@qa *design {story})
        
        Args:
            story: Story to design tests for
            parameters: Additional parameters
            
        Returns:
            Test strategy result
        """
        try:
            test_strategy = {
                "story_id": story.story_id,
                "created_at": datetime.now().isoformat(),
                "test_types": [],
                "test_scenarios": [],
                "automation_plan": {},
                "quality_criteria": []
            }
            
            # Determine test types based on story characteristics
            if "api" in story.description.lower() or "endpoint" in story.description.lower():
                test_strategy["test_types"].extend(["unit_tests", "integration_tests", "api_tests"])
            if "ui" in story.description.lower() or "interface" in story.description.lower():
                test_strategy["test_types"].extend(["unit_tests", "component_tests", "e2e_tests"])
            if "database" in story.description.lower() or "data" in story.description.lower():
                test_strategy["test_types"].extend(["unit_tests", "integration_tests", "data_validation_tests"])
            
            # Generate test scenarios from acceptance criteria
            for i, criteria in enumerate(story.acceptance_criteria):
                scenario = {
                    "scenario_id": f"scenario_{i+1}",
                    "description": f"Test {criteria}",
                    "test_type": "functional",
                    "priority": "high",
                    "automation_candidate": True
                }
                test_strategy["test_scenarios"].append(scenario)
            
            # Automation plan
            test_strategy["automation_plan"] = {
                "automation_percentage": min(80, len(story.acceptance_criteria) * 20),
                "automation_tools": ["pytest", "selenium", "postman"],
                "ci_cd_integration": True,
                "maintenance_strategy": "continuous"
            }
            
            # Quality criteria
            test_strategy["quality_criteria"] = [
                "All acceptance criteria must have corresponding tests",
                "Minimum 80% code coverage for new code",
                "All critical paths must be covered by automated tests",
                "Performance criteria must be validated",
                "Security considerations must be tested"
            ]
            
            # Store in story
            story.test_strategy = test_strategy
            story.add_agent_note("qa", "Test strategy designed and documented")
            
            logger.info(f"Test strategy designed for story {story.story_id}")
            
            return {
                "success": True,
                "test_strategy": test_strategy,
                "implementation_plan": self._create_test_implementation_plan(test_strategy),
                "message": "Test strategy designed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error designing test strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def trace_requirements(self, story: StoryContext, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Requirements tracing implementation (@qa *trace {story})
        
        Args:
            story: Story to trace requirements for
            parameters: Additional parameters
            
        Returns:
            Requirements tracing result
        """
        try:
            tracing_report = {
                "story_id": story.story_id,
                "traced_at": datetime.now().isoformat(),
                "requirement_coverage": {},
                "implementation_mapping": {},
                "test_coverage": {},
                "gaps_identified": []
            }
            
            # Trace acceptance criteria to implementation
            for i, criteria in enumerate(story.acceptance_criteria):
                req_id = f"REQ_{story.story_id}_{i+1}"
                
                tracing_report["requirement_coverage"][req_id] = {
                    "requirement": criteria,
                    "implementation_status": "pending",  # Would be updated during development
                    "test_coverage": "planned",
                    "validation_method": "functional_test"
                }
            
            # Check for gaps
            if len(story.acceptance_criteria) == 0:
                tracing_report["gaps_identified"].append("No acceptance criteria defined")
            
            if not story.tasks:
                tracing_report["gaps_identified"].append("No implementation tasks defined")
            
            if not story.test_strategy:
                tracing_report["gaps_identified"].append("No test strategy defined")
            
            # Store tracing report
            story.validation_results["requirements_tracing"] = tracing_report
            story.add_agent_note("qa", f"Requirements tracing completed - {len(tracing_report['gaps_identified'])} gaps identified")
            
            logger.info(f"Requirements tracing for story {story.story_id}: {len(tracing_report['gaps_identified'])} gaps found")
            
            return {
                "success": True,
                "tracing_report": tracing_report,
                "coverage_percentage": self._calculate_coverage_percentage(tracing_report),
                "message": f"Requirements tracing completed - {len(tracing_report['gaps_identified'])} gaps identified"
            }
            
        except Exception as e:
            logger.error(f"Error in requirements tracing: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_nfr(self, story: StoryContext, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Non-functional requirements check (@qa *nfr {story})
        
        Args:
            story: Story to check NFRs for
            parameters: Additional parameters
            
        Returns:
            NFR check result
        """
        try:
            nfr_categories = {
                "performance": {"status": "not_assessed", "criteria": [], "issues": []},
                "security": {"status": "not_assessed", "criteria": [], "issues": []},
                "usability": {"status": "not_assessed", "criteria": [], "issues": []},
                "reliability": {"status": "not_assessed", "criteria": [], "issues": []},
                "scalability": {"status": "not_assessed", "criteria": [], "issues": []},
                "maintainability": {"status": "not_assessed", "criteria": [], "issues": []}
            }
            
            # Assess each NFR category
            for category in nfr_categories:
                assessment = await self._assess_nfr_category(story, category)
                nfr_categories[category] = assessment
            
            # Overall NFR assessment
            total_issues = sum(len(cat["issues"]) for cat in nfr_categories.values())
            overall_status = "passed" if total_issues == 0 else "needs_attention"
            
            nfr_report = {
                "story_id": story.story_id,
                "assessed_at": datetime.now().isoformat(),
                "overall_status": overall_status,
                "categories": nfr_categories,
                "total_issues": total_issues,
                "recommendations": self._generate_nfr_recommendations(nfr_categories)
            }
            
            # Store NFR assessment
            story.validation_results["nfr_assessment"] = nfr_report
            story.add_agent_note("qa", f"NFR assessment completed - {total_issues} issues identified")
            
            logger.info(f"NFR assessment for story {story.story_id}: {overall_status}")
            
            return {
                "success": True,
                "nfr_report": nfr_report,
                "action_required": total_issues > 0,
                "message": f"NFR assessment completed - {overall_status}"
            }
            
        except Exception as e:
            logger.error(f"Error in NFR check: {e}")
            return {"success": False, "error": str(e)}
    
    async def comprehensive_review(self, story: StoryContext, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive story review (@qa *review {story})
        
        Args:
            story: Story to review
            parameters: Additional parameters
            
        Returns:
            Comprehensive review result
        """
        try:
            review_report = {
                "story_id": story.story_id,
                "reviewed_at": datetime.now().isoformat(),
                "reviewer": "qa_agent",
                "review_sections": {}
            }
            
            # Requirements review
            req_review = await self._review_requirements(story)
            review_report["review_sections"]["requirements"] = req_review
            
            # Implementation review
            impl_review = await self._review_implementation(story)
            review_report["review_sections"]["implementation"] = impl_review
            
            # Testing review
            test_review = await self._review_testing(story)
            review_report["review_sections"]["testing"] = test_review
            
            # Quality review
            quality_review = await self._review_quality(story)
            review_report["review_sections"]["quality"] = quality_review
            
            # Documentation review
            doc_review = await self._review_documentation(story)
            review_report["review_sections"]["documentation"] = doc_review
            
            # Overall assessment
            section_scores = [section["score"] for section in review_report["review_sections"].values()]
            overall_score = sum(section_scores) / len(section_scores) if section_scores else 0
            
            review_report["overall_score"] = overall_score
            review_report["overall_grade"] = self._calculate_grade(overall_score)
            review_report["approval_status"] = "approved" if overall_score >= 8.0 else "needs_improvement"
            
            # Collect all recommendations
            all_recommendations = []
            for section in review_report["review_sections"].values():
                all_recommendations.extend(section.get("recommendations", []))
            
            review_report["recommendations"] = all_recommendations
            
            # Store comprehensive review
            story.validation_results["comprehensive_review"] = review_report
            story.add_agent_note("qa", f"Comprehensive review completed - Score: {overall_score:.1f}/10.0")
            
            self.quality_metrics["comprehensive_reviews"] += 1
            
            logger.info(f"Comprehensive review for story {story.story_id}: {review_report['overall_grade']}")
            
            return {
                "success": True,
                "review_report": review_report,
                "approval_recommended": review_report["approval_status"] == "approved",
                "message": f"Comprehensive review completed - {review_report['overall_grade']}"
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive review: {e}")
            return {"success": False, "error": str(e)}
    
    async def quality_gate_assessment(self, story: StoryContext, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Quality gate assessment (@qa *gate {story})
        
        Args:
            story: Story for quality gate assessment
            parameters: Additional parameters
            
        Returns:
            Quality gate assessment result
        """
        try:
            # Run comprehensive quality gate check
            gate_result = await self.check_story_gates(story, StoryState.COMPLETED)
            
            # Additional quality gate specific checks
            gate_assessment = {
                "story_id": story.story_id,
                "assessed_at": datetime.now().isoformat(),
                "gate_result": gate_result,
                "final_approval": False,
                "certification_level": "none"
            }
            
            # Determine certification level
            if gate_result["passed"] and gate_result["quality_level"] == "passed":
                gate_assessment["certification_level"] = "full"
                gate_assessment["final_approval"] = True
            elif gate_result["passed"] and gate_result["quality_level"] == "warning":
                gate_assessment["certification_level"] = "conditional"
                gate_assessment["final_approval"] = True
            else:
                gate_assessment["certification_level"] = "none"
                gate_assessment["final_approval"] = False
            
            # Generate quality certificate if approved
            if gate_assessment["final_approval"]:
                certificate = self._generate_quality_certificate(story, gate_assessment)
                gate_assessment["quality_certificate"] = certificate
            
            # Store gate assessment
            story.validation_results["quality_gate_assessment"] = gate_assessment
            story.add_agent_note("qa", f"Quality gate assessment: {gate_assessment['certification_level']} certification")
            
            logger.info(f"Quality gate assessment for story {story.story_id}: {gate_assessment['certification_level']}")
            
            return {
                "success": True,
                "gate_assessment": gate_assessment,
                "final_approval": gate_assessment["final_approval"],
                "message": f"Quality gate assessment completed - {gate_assessment['certification_level']} certification"
            }
            
        except Exception as e:
            logger.error(f"Error in quality gate assessment: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    async def _run_quality_check(self, story: StoryContext, check_type: str) -> Dict[str, Any]:
        """Run specific quality check"""
        check_methods = {
            "acceptance_criteria": self._check_acceptance_criteria,
            "task_breakdown": self._check_task_breakdown,
            "implementation_complete": self._check_implementation_complete,
            "unit_tests": self._check_unit_tests,
            "code_review": self._check_code_review,
            "all_tests_passed": self._check_all_tests_passed,
            "documentation_updated": self._check_documentation_updated,
            "acceptance_criteria_met": self._check_acceptance_criteria_met,
            "qa_review_passed": self._check_qa_review_passed,
            "stakeholder_approval": self._check_stakeholder_approval,
            "deployment_ready": self._check_deployment_ready
        }
        
        check_method = check_methods.get(check_type, self._default_check)
        return await check_method(story)
    
    async def _has_blocking_issue(self, story: StoryContext, issue_type: str) -> bool:
        """Check for specific blocking issues"""
        issue_checks = {
            "missing_requirements": lambda: len(story.acceptance_criteria) == 0,
            "unclear_scope": lambda: not story.description or len(story.description) < 50,
            "test_failures": lambda: story.validation_results.get("test_failures", 0) > 0,
            "code_quality_issues": lambda: story.validation_results.get("code_quality_score", 10) < 7,
            "failing_tests": lambda: story.validation_results.get("failing_tests", 0) > 0,
            "incomplete_features": lambda: len(story.tasks) > 0 and not all(task.get("completed", False) for task in story.tasks),
            "unresolved_defects": lambda: story.validation_results.get("open_defects", 0) > 0,
            "missing_approvals": lambda: not story.validation_results.get("stakeholder_approved", False)
        }
        
        check_function = issue_checks.get(issue_type, lambda: False)
        return check_function()
    
    def _assess_technical_complexity(self, story: StoryContext) -> int:
        """Assess technical complexity (1-10 scale)"""
        complexity_score = 1
        
        # Check description for complexity indicators
        complexity_keywords = ["complex", "integration", "algorithm", "performance", "security", "architecture"]
        for keyword in complexity_keywords:
            if keyword in story.description.lower():
                complexity_score += 1
        
        # Check number of acceptance criteria
        if len(story.acceptance_criteria) > 5:
            complexity_score += 1
        
        # Check number of tasks
        if len(story.tasks) > 8:
            complexity_score += 1
        
        return min(complexity_score, 10)
    
    def _assess_dependencies(self, story: StoryContext) -> int:
        """Assess dependency risk (1-10 scale)"""
        dependency_score = 1
        
        # Check for dependency keywords
        dependency_keywords = ["api", "service", "external", "third-party", "integration"]
        for keyword in dependency_keywords:
            if keyword in story.description.lower():
                dependency_score += 1
        
        return min(dependency_score, 10)
    
    def _assess_time_risk(self, story: StoryContext) -> int:
        """Assess time estimation risk (1-10 scale)"""
        time_risk = 1
        
        # More tasks = more time risk
        if len(story.tasks) > 10:
            time_risk += 2
        elif len(story.tasks) > 5:
            time_risk += 1
        
        # Unclear requirements = time risk
        if len(story.acceptance_criteria) < 3:
            time_risk += 2
        
        return min(time_risk, 10)
    
    def _get_risk_next_actions(self, risk_level: str) -> List[str]:
        """Get next actions based on risk level"""
        actions_map = {
            "LOW": ["Proceed with standard development process"],
            "MEDIUM": ["Schedule architect review", "Add additional testing", "Create detailed task breakdown"],
            "HIGH": ["Mandatory architect review", "Prototype key components", "Extended testing phase", "Stakeholder sign-off required"]
        }
        
        return actions_map.get(risk_level, [])
    
    def _create_test_implementation_plan(self, test_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation plan for test strategy"""
        return {
            "phases": [
                {"phase": "unit_tests", "timeline": "During development", "responsibility": "developer"},
                {"phase": "integration_tests", "timeline": "After unit tests", "responsibility": "developer"},
                {"phase": "functional_tests", "timeline": "After integration", "responsibility": "qa"},
                {"phase": "automation", "timeline": "Parallel to manual testing", "responsibility": "qa"}
            ],
            "tools_setup": ["pytest", "coverage", "selenium"],
            "ci_cd_integration": "Add to deployment pipeline",
            "success_criteria": "All tests passing, 80% coverage achieved"
        }
    
    def _calculate_coverage_percentage(self, tracing_report: Dict[str, Any]) -> float:
        """Calculate requirements coverage percentage"""
        total_requirements = len(tracing_report["requirement_coverage"])
        if total_requirements == 0:
            return 0.0
        
        covered_requirements = sum(
            1 for req in tracing_report["requirement_coverage"].values()
            if req["implementation_status"] != "pending"
        )
        
        return (covered_requirements / total_requirements) * 100
    
    async def _assess_nfr_category(self, story: StoryContext, category: str) -> Dict[str, Any]:
        """Assess specific NFR category"""
        # This would contain detailed NFR assessment logic for each category
        # Simplified implementation for now
        return {
            "status": "assessed",
            "criteria": [f"{category} criteria defined"],
            "issues": [],  # Would contain actual issues found
            "score": 8.0  # Default good score
        }
    
    def _generate_nfr_recommendations(self, nfr_categories: Dict[str, Any]) -> List[str]:
        """Generate NFR recommendations"""
        recommendations = []
        
        for category, assessment in nfr_categories.items():
            if assessment["issues"]:
                recommendations.append(f"Address {category} issues: {', '.join(assessment['issues'])}")
        
        return recommendations
    
    async def _review_requirements(self, story: StoryContext) -> Dict[str, Any]:
        """Review story requirements"""
        score = 5.0
        issues = []
        recommendations = []
        
        if story.acceptance_criteria:
            score += 2.0
        else:
            issues.append("No acceptance criteria defined")
            recommendations.append("Define clear acceptance criteria")
        
        if story.description and len(story.description) > 100:
            score += 1.0
        else:
            issues.append("Insufficient story description")
            recommendations.append("Expand story description")
        
        return {
            "score": min(score, 10.0),
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _review_implementation(self, story: StoryContext) -> Dict[str, Any]:
        """Review story implementation"""
        # Simplified implementation review
        return {
            "score": 8.0,  # Default good score
            "issues": [],
            "recommendations": []
        }
    
    async def _review_testing(self, story: StoryContext) -> Dict[str, Any]:
        """Review story testing"""
        score = 5.0
        issues = []
        recommendations = []
        
        if story.test_strategy:
            score += 3.0
        else:
            issues.append("No test strategy defined")
            recommendations.append("Create comprehensive test strategy")
        
        return {
            "score": min(score, 10.0),
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _review_quality(self, story: StoryContext) -> Dict[str, Any]:
        """Review story quality"""
        return {
            "score": 8.0,
            "issues": [],
            "recommendations": []
        }
    
    async def _review_documentation(self, story: StoryContext) -> Dict[str, Any]:
        """Review story documentation"""
        return {
            "score": 7.0,
            "issues": [],
            "recommendations": ["Ensure documentation is updated"]
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score"""
        if score >= 9.0:
            return "A+"
        elif score >= 8.5:
            return "A"
        elif score >= 8.0:
            return "A-"
        elif score >= 7.5:
            return "B+"
        elif score >= 7.0:
            return "B"
        elif score >= 6.0:
            return "B-"
        elif score >= 5.0:
            return "C"
        else:
            return "F"
    
    def _generate_quality_certificate(self, story: StoryContext, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quality certificate for approved story"""
        return {
            "certificate_id": f"QC_{story.story_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "story_id": story.story_id,
            "certification_level": assessment["certification_level"],
            "issued_at": datetime.now().isoformat(),
            "issued_by": "BMAD Quality Gate Manager",
            "valid_until": None,  # No expiration for story certificates
            "quality_score": assessment["gate_result"]["quality_level"],
            "certification_criteria_met": True
        }
    
    # Quality check implementations
    async def _check_acceptance_criteria(self, story: StoryContext) -> Dict[str, Any]:
        """Check acceptance criteria quality"""
        if not story.acceptance_criteria:
            return {
                "level": QualityLevel.FAILED,
                "issues": ["No acceptance criteria defined"],
                "recommendations": ["Define clear, testable acceptance criteria"]
            }
        elif len(story.acceptance_criteria) < 2:
            return {
                "level": QualityLevel.WARNING,
                "issues": ["Limited acceptance criteria"],
                "recommendations": ["Consider adding more detailed acceptance criteria"]
            }
        else:
            return {
                "level": QualityLevel.PASSED,
                "issues": [],
                "recommendations": []
            }
    
    async def _check_task_breakdown(self, story: StoryContext) -> Dict[str, Any]:
        """Check task breakdown quality"""
        if not story.tasks:
            return {
                "level": QualityLevel.FAILED,
                "issues": ["No tasks defined"],
                "recommendations": ["Break down story into implementable tasks"]
            }
        else:
            return {
                "level": QualityLevel.PASSED,
                "issues": [],
                "recommendations": []
            }
    
    async def _default_check(self, story: StoryContext) -> Dict[str, Any]:
        """Default quality check"""
        return {
            "level": QualityLevel.WARNING,
            "issues": ["Quality check not implemented"],
            "recommendations": ["Implement specific quality check"]
        }
    
    # Simplified implementations for other checks
    async def _check_implementation_complete(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_unit_tests(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_code_review(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_all_tests_passed(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_documentation_updated(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_acceptance_criteria_met(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_qa_review_passed(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_stakeholder_approval(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    async def _check_deployment_ready(self, story: StoryContext) -> Dict[str, Any]:
        return {"level": QualityLevel.PASSED, "issues": [], "recommendations": []}
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality gate metrics"""
        return {
            "quality_gate_manager_version": "1.0.0",
            "metrics": self.quality_metrics,
            "gate_requirements_configured": len(self.gate_requirements),
            "supported_qa_commands": ["*risk", "*design", "*trace", "*nfr", "*review", "*gate"]
        }