"""
Staging Deployment Configuration & Scripts

Automated deployment to staging environment with verification.
"""

import os
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class StagingDeployer:
    """Deploy production hardening system to staging"""
    
    def __init__(self, staging_dir: Optional[str] = None):
        self.staging_dir = Path(staging_dir or "/opt/legal_finance_rag/staging")
        self.timestamp = datetime.now().isoformat()
        self.deployment_log = []
        self.workspace_root = Path(__file__).parent.parent.parent
    
    def pre_deployment_checks(self) -> bool:
        """Verify all production systems are ready for deployment"""
        
        checks = {
            "app/tools/compliance.py": "Compliance module",
            "app/tools/audit_logger.py": "Audit logger",
            "app/tools/rate_limiter.py": "Rate limiter",
            "app/tools/cache_layer.py": "Cache layer",
            "app/tools/input_validator.py": "Input validator",
            "app/tools/executor.py": "Enhanced executor",
        }
        
        print("🔍 Pre-Deployment Verification")
        print("=" * 60)
        
        all_ready = True
        for file_path, description in checks.items():
            full_path = self.workspace_root / file_path
            if full_path.exists():
                print(f"✅ {description}: Found")
                self._log(f"✅ {description} verified")
            else:
                print(f"❌ {description}: MISSING at {full_path}")
                all_ready = False
                self._log(f"❌ {description} NOT FOUND")
        
        print("=" * 60)
        return all_ready
    
    def prepare_staging_environment(self) -> bool:
        """Prepare staging directory structure"""
        
        print("\n📁 Preparing Staging Environment")
        print("=" * 60)
        
        try:
            # Create staging directories
            dirs_to_create = [
                self.staging_dir,
                self.staging_dir / "app" / "tools",
                self.staging_dir / "data" / "reference",
                self.staging_dir / "logs" / "audit",
                self.staging_dir / "cache",
                self.staging_dir / "config",
                self.staging_dir / "tests"
            ]
            
            for dir_path in dirs_to_create:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created: {dir_path}")
                self._log(f"✅ Created directory: {dir_path}")
            
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Error preparing environment: {e}")
            self._log(f"❌ Error: {e}")
            return False
    
    def deploy_production_modules(self) -> bool:
        """Deploy all production hardening modules to staging"""
        
        print("\n📦 Deploying Production Modules")
        print("=" * 60)
        
        modules = [
            ("app/tools/compliance.py", "Compliance Manager"),
            ("app/tools/audit_logger.py", "Audit Logger"),
            ("app/tools/rate_limiter.py", "Rate Limiter"),
            ("app/tools/cache_layer.py", "Cache Layer"),
            ("app/tools/input_validator.py", "Input Validator"),
            ("app/tools/executor.py", "Enhanced Executor"),
        ]
        
        try:
            for src_file, description in modules:
                src_path = self.workspace_root / src_file
                dst_path = self.staging_dir / src_file
                
                if src_path.exists():
                    # Ensure destination directory exists
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_path, dst_path)
                    print(f"✅ Deployed: {description} ({src_file})")
                    self._log(f"✅ Deployed {description}")
                else:
                    print(f"❌ Source not found: {src_file}")
                    self._log(f"❌ Source missing: {src_file}")
                    return False
            
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            self._log(f"❌ Deployment error: {e}")
            return False
    
    def deploy_test_suite(self) -> bool:
        """Deploy test suite to staging"""
        
        print("\n🧪 Deploying Test Suite")
        print("=" * 60)
        
        try:
            test_src = self.workspace_root / "tests/test_production_hardening.py"
            test_dst = self.staging_dir / "tests" / "test_production_hardening.py"
            
            if test_src.exists():
                test_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(test_src, test_dst)
                print(f"✅ Deployed: Test Suite")
                self._log("✅ Test suite deployed")
                
                print("=" * 60)
                return True
            else:
                print(f"❌ Test suite not found")
                self._log("❌ Test suite not found")
                return False
                
        except Exception as e:
            print(f"❌ Error deploying tests: {e}")
            self._log(f"❌ Error: {e}")
            return False
    
    def create_staging_config(self) -> bool:
        """Create staging configuration file"""
        
        print("\n⚙️  Creating Staging Configuration")
        print("=" * 60)
        
        try:
            config = {
                "environment": "staging",
                "deployed_at": self.timestamp,
                "version": "1.0.0",
                "systems": {
                    "compliance_manager": {
                        "enabled": True,
                        "include_disclaimers": True,
                        "data_max_age_days": 180
                    },
                    "audit_logger": {
                        "enabled": True,
                        "log_directory": str(self.staging_dir / "logs" / "audit"),
                        "rotation": "daily",
                        "retention_days": 90
                    },
                    "rate_limiter": {
                        "enabled": True,
                        "default_per_hour": 100,
                        "default_per_minute": 10
                    },
                    "cache_layer": {
                        "enabled": True,
                        "cache_dir": str(self.staging_dir / "cache"),
                        "max_size": 1000,
                        "eviction": "lru"
                    },
                    "input_validator": {
                        "enabled": True,
                        "strict_mode": True
                    }
                },
                "monitoring": {
                    "enabled": True,
                    "metrics_interval_seconds": 60,
                    "alert_on_error_rate": 0.05
                }
            }
            
            config_file = self.staging_dir / "config" / "staging.json"
            config_file.write_text(json.dumps(config, indent=2))
            
            print(f"✅ Configuration created: {config_file}")
            self._log(f"✅ Staging config created")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Error creating config: {e}")
            self._log(f"❌ Config error: {e}")
            return False
    
    def run_staging_tests(self) -> bool:
        """Run test suite in staging environment"""
        
        print("\n🧪 Running Staging Tests")
        print("=" * 60)
        
        try:
            test_file = self.staging_dir / "tests" / "test_production_hardening.py"
            
            if not test_file.exists():
                print(f"❌ Test file not found: {test_file}")
                return False
            
            # Note: In real deployment, would run pytest here
            print("✅ Test suite ready for execution")
            print("   Command: pytest tests/test_production_hardening.py -v")
            self._log("✅ Tests staged for execution")
            
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            self._log(f"❌ Test error: {e}")
            return False
    
    def create_deployment_summary(self) -> Dict:
        """Create deployment summary"""
        
        summary = {
            "timestamp": self.timestamp,
            "environment": "staging",
            "staging_directory": str(self.staging_dir),
            "modules_deployed": 6,
            "log_file": str(self.staging_dir / "deployment.log"),
            "status": "READY FOR TESTING",
            "next_steps": [
                "1. Run full test suite: pytest tests/test_production_hardening.py -v",
                "2. Performance baseline testing",
                "3. Load testing with 10-100 concurrent users",
                "4. Integration testing with all 6 tools",
                "5. Security audit of audit logs and data handling"
            ]
        }
        
        return summary
    
    def write_deployment_log(self):
        """Write deployment log"""
        
        log_file = self.staging_dir / "deployment.log"
        
        with open(log_file, 'w') as f:
            f.write("STAGING DEPLOYMENT LOG\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write("=" * 60 + "\n\n")
            
            for entry in self.deployment_log:
                f.write(entry + "\n")
    
    def _log(self, message: str):
        """Add message to deployment log"""
        self.deployment_log.append(f"[{datetime.now().isoformat()}] {message}")
    
    def deploy(self) -> bool:
        """Execute full deployment"""
        
        print("\n" + "=" * 60)
        print("STAGING ENVIRONMENT DEPLOYMENT")
        print("=" * 60)
        
        steps = [
            ("Pre-deployment checks", self.pre_deployment_checks),
            ("Prepare environment", self.prepare_staging_environment),
            ("Deploy modules", self.deploy_production_modules),
            ("Deploy tests", self.deploy_test_suite),
            ("Create config", self.create_staging_config),
            ("Stage tests", self.run_staging_tests),
        ]
        
        all_success = True
        for step_name, step_func in steps:
            success = step_func()
            if not success:
                print(f"\n❌ Deployment failed at: {step_name}")
                all_success = False
                break
        
        if all_success:
            summary = self.create_deployment_summary()
            self.write_deployment_log()
            
            print("\n" + "=" * 60)
            print("✅ STAGING DEPLOYMENT SUCCESSFUL")
            print("=" * 60)
            print(json.dumps(summary, indent=2))
            
            return True
        else:
            self.write_deployment_log()
            return False


def main():
    """Main deployment script"""
    
    deployer = StagingDeployer()
    success = deployer.deploy()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
