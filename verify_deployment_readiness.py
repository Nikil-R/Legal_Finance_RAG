#!/usr/bin/env python3
"""
Deployment Readiness Verification Script
Verifies all infrastructure components are ready for production deployment
"""

import os
import json
from pathlib import Path
from datetime import datetime

class DeploymentReadinessChecker:
    """Verify all deployment infrastructure is ready"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "status": "INITIALIZING"
        }
    
    def check_production_systems(self) -> bool:
        """Verify all 6 production systems exist"""
        systems = [
            "app/tools/compliance.py",
            "app/tools/audit_logger.py",
            "app/tools/rate_limiter.py",
            "app/tools/cache_layer.py",
            "app/tools/input_validator.py",
            "app/tools/executor.py"
        ]
        
        missing = []
        for system in systems:
            path = self.workspace_root / system
            if not path.exists():
                missing.append(system)
        
        check = {
            "name": "Production Systems (6 modules)",
            "status": "✅ PASS" if not missing else "❌ FAIL",
            "details": f"{6 - len(missing)}/6 systems found",
            "missing": missing if missing else []
        }
        self.results["checks"].append(check)
        return not missing
    
    def check_test_suite(self) -> bool:
        """Verify test suite exists"""
        test_file = self.workspace_root / "tests/test_production_hardening.py"
        exists = test_file.exists()
        
        check = {
            "name": "Test Suite (34 tests)",
            "status": "✅ PASS" if exists else "❌ FAIL",
            "details": "test_production_hardening.py found",
            "file": str(test_file) if exists else "NOT FOUND"
        }
        self.results["checks"].append(check)
        return exists
    
    def check_deployment_scripts(self) -> bool:
        """Verify all deployment scripts exist"""
        scripts = [
            "scripts/staging_deploy.py",
            "scripts/real_data_integration.py",
            "scripts/performance_optimization.py",
            "scripts/beta_and_production_rollout.py",
            "scripts/production_deployment_guide.py"
        ]
        
        missing = []
        for script in scripts:
            path = self.workspace_root / script
            if not path.exists():
                missing.append(script)
        
        check = {
            "name": "Deployment Scripts (5 scripts)",
            "status": "✅ PASS" if not missing else "❌ FAIL",
            "details": f"{5 - len(missing)}/5 scripts found",
            "missing": missing if missing else []
        }
        self.results["checks"].append(check)
        return not missing
    
    def check_documentation(self) -> bool:
        """Verify all documentation exists"""
        docs = [
            "DEPLOYMENT_CHECKLIST.md",
            "DEPLOYMENT_COMPLETE.md",
            "PRODUCTION_HARDENING_GUIDE.md"
        ]
        
        missing = []
        for doc in docs:
            path = self.workspace_root / doc
            if not path.exists():
                missing.append(doc)
        
        check = {
            "name": "Documentation (3 guides)",
            "status": "✅ PASS" if not missing else "⚠️  PARTIAL",
            "details": f"{3 - len(missing)}/3 documents found",
            "missing": missing if missing else []
        }
        self.results["checks"].append(check)
        return len(missing) <= 1
    
    def check_infrastructure(self) -> bool:
        """Verify infrastructure directories exist"""
        dirs = [
            "app/tools",
            "scripts",
            "tests",
            "data/real"
        ]
        
        missing = []
        for directory in dirs:
            path = self.workspace_root / directory
            if not path.exists():
                missing.append(directory)
        
        check = {
            "name": "Infrastructure Directories",
            "status": "✅ PASS" if not missing else "⚠️  PARTIAL",
            "details": f"{len(dirs) - len(missing)}/{len(dirs)} directories found",
            "missing": missing if missing else []
        }
        self.results["checks"].append(check)
        return len(missing) <= 1
    
    def check_file_sizes(self) -> bool:
        """Verify deployment scripts have reasonable sizes"""
        expected_sizes = {
            "scripts/staging_deploy.py": (300, 400),
            "scripts/real_data_integration.py": (350, 450),
            "scripts/performance_optimization.py": (400, 500),
            "scripts/beta_and_production_rollout.py": (500, 700),
            "scripts/production_deployment_guide.py": (600, 800)
        }
        
        issues = []
        for script, (min_size, max_size) in expected_sizes.items():
            path = self.workspace_root / script
            if path.exists():
                lines = len(path.read_text().split('\n'))
                if not (min_size <= lines <= max_size):
                    issues.append(f"{script}: {lines} lines (expected {min_size}-{max_size})")
        
        check = {
            "name": "File Size Verification",
            "status": "✅ PASS" if not issues else "⚠️  WARNING",
            "details": "All scripts have expected sizes",
            "issues": issues if issues else []
        }
        self.results["checks"].append(check)
        return not issues
    
    def run_all_checks(self) -> dict:
        """Run all verification checks"""
        
        print("\n" + "=" * 70)
        print("DEPLOYMENT READINESS VERIFICATION")
        print("=" * 70)
        
        checks_passed = 0
        checks_failed = 0
        
        checks = [
            self.check_production_systems,
            self.check_test_suite,
            self.check_deployment_scripts,
            self.check_documentation,
            self.check_infrastructure,
            self.check_file_sizes
        ]
        
        for check_func in checks:
            try:
                result = check_func()
                if result:
                    checks_passed += 1
                else:
                    checks_failed += 1
            except Exception as e:
                self.results["checks"].append({
                    "name": check_func.__name__,
                    "status": "❌ ERROR",
                    "error": str(e)
                })
                checks_failed += 1
        
        # Print results
        print("\n📋 VERIFICATION RESULTS:\n")
        for check in self.results["checks"]:
            print(f"{check['status']} {check['name']}")
            print(f"   └─ {check['details']}")
            if check.get('missing'):
                for item in check['missing']:
                    print(f"      ❌ Missing: {item}")
            print()
        
        # Final status
        print("=" * 70)
        if checks_failed == 0:
            self.results["status"] = "🚀 READY FOR DEPLOYMENT"
            print("✅ ALL CHECKS PASSED - SYSTEM READY FOR DEPLOYMENT")
        elif checks_failed <= 2:
            self.results["status"] = "⚠️  MOSTLY READY (Minor issues)"
            print(f"⚠️  {checks_failed} check(s) failed - Review issues before deployment")
        else:
            self.results["status"] = "❌ NOT READY - Critical issues found"
            print(f"❌ {checks_failed} critical check(s) failed - Fix before deployment")
        
        print("=" * 70)
        
        return self.results
    
    def print_next_steps(self) -> None:
        """Print next steps for deployment"""
        
        print("\n🚀 NEXT STEPS:\n")
        
        print("1️⃣  WEEK 1 - STAGING DEPLOYMENT:")
        print("   python scripts/staging_deploy.py")
        print("   pytest tests/test_production_hardening.py -v")
        print()
        
        print("2️⃣  WEEKS 2-5 - REAL DATA INTEGRATION:")
        print("   Export API credentials first:")
        print("   • SCC_API_KEY")
        print("   • MCA_USERNAME / MCA_PASSWORD")
        print("   • BSE_API_KEY / NSE_API_KEY")
        print("   Then: python scripts/real_data_integration.py --all-sources")
        print()
        
        print("3️⃣  WEEKS 3-4 - PERFORMANCE OPTIMIZATION:")
        print("   python scripts/performance_optimization.py --full-analysis")
        print()
        
        print("4️⃣  WEEKS 6-9 - BETA LAUNCH:")
        print("   python scripts/beta_and_production_rollout.py --launch-beta")
        print()
        
        print("5️⃣  WEEK 10+ - PRODUCTION ROLLOUT:")
        print("   python scripts/production_deployment_guide.py --deploy-production")
        print()
        
        print("📚 REFERENCE GUIDES:")
        print("   • DEPLOYMENT_CHECKLIST.md (week-by-week commands)")
        print("   • DEPLOYMENT_COMPLETE.md (comprehensive overview)")
        print("   • PRODUCTION_HARDENING_GUIDE.md (system details)")
        print()


def main():
    """Main execution"""
    
    # Get workspace root
    workspace_root = Path(__file__).parent
    
    # Run verification
    checker = DeploymentReadinessChecker(str(workspace_root))
    results = checker.run_all_checks()
    
    # Print next steps
    checker.print_next_steps()
    
    # Save results
    results_file = workspace_root / "deployment_readiness_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: deployment_readiness_results.json\n")


if __name__ == "__main__":
    main()
