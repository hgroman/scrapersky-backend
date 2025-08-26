#!/usr/bin/env python3
"""
WF6 Component Testing Script
Test Sentinel: Layer 7 Testing Guardian
Version: 1.0

This script provides granular component testing for WF6 workflow components.
Can be used standalone or as part of the complete test suite.
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import yaml
import asyncpg
import httpx


class WF6ComponentTester:
    """Component-by-component tester for WF6 workflow"""
    
    def __init__(self):
        self.test_results = {
            "test_run_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "component_tests": {},
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "scrapersky_db",
            "user": "scrapersky_user",
            "password": "scrapersky_password"
        }
        self.api_base = "http://localhost:8000"
        self.jwt_token = None
    
    async def setup(self):
        """Setup test environment and authentication"""
        print("🔧 Setting up component tester...")
        
        # Generate JWT token
        try:
            async with httpx.AsyncClient() as client:
                auth_response = await client.post(
                    f"{self.api_base}/auth/login",
                    json={"username": "test_user", "password": "test_pass"}
                )
                if auth_response.status_code == 200:
                    self.jwt_token = auth_response.json().get("access_token")
                    print("✅ JWT token generated")
                else:
                    print("⚠️ JWT generation failed, using mock token")
                    self.jwt_token = "mock_token_for_testing"
        except Exception as e:
            print(f"⚠️ Auth setup failed: {e}")
            self.jwt_token = "mock_token_for_testing"
    
    def record_test(self, component: str, test_name: str, status: str, message: str):
        """Record test result"""
        if component not in self.test_results["component_tests"]:
            self.test_results["component_tests"][component] = {}
        
        self.test_results["component_tests"][component][test_name] = {
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.test_results["summary"]["total"] += 1
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1
    
    async def test_database_connectivity(self):
        """Test database connection and table access"""
        print("\n🗄️ Testing Database Connectivity")
        print("================================")
        
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            # Test basic connection
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                print("✅ Database connection successful")
                self.record_test("database", "connection", "PASS", "Database connection established")
            else:
                print("❌ Database connection failed")
                self.record_test("database", "connection", "FAIL", "Database connection test failed")
                return
            
            # Test required tables
            required_tables = ["domains", "sitemap_files", "pages"]
            for table in required_tables:
                try:
                    await conn.fetchval(f"SELECT 1 FROM {table} LIMIT 1")
                    print(f"✅ Table '{table}' accessible")
                    self.record_test("database", f"table_{table}", "PASS", f"Table {table} exists and accessible")
                except Exception as e:
                    print(f"❌ Table '{table}' not accessible: {e}")
                    self.record_test("database", f"table_{table}", "FAIL", f"Table {table} not accessible: {e}")
            
            # Test enum types
            try:
                result = await conn.fetch("""
                    SELECT enumlabel FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'sitemap_import_process_status_enum')
                """)
                enum_values = [row['enumlabel'] for row in result]
                expected_values = ['Queued', 'Processing', 'Complete', 'Error']
                
                if all(val in enum_values for val in expected_values):
                    print("✅ SitemapImportProcessStatusEnum validation passed")
                    self.record_test("database", "status_enum", "PASS", f"Enum values: {enum_values}")
                else:
                    print(f"❌ SitemapImportProcessStatusEnum missing values. Found: {enum_values}")
                    self.record_test("database", "status_enum", "FAIL", f"Missing enum values. Found: {enum_values}")
            except Exception as e:
                print(f"❌ Enum validation failed: {e}")
                self.record_test("database", "status_enum", "FAIL", f"Enum validation failed: {e}")
            
            await conn.close()
            
        except Exception as e:
            print(f"❌ Database connectivity test failed: {e}")
            self.record_test("database", "connection", "FAIL", f"Database connectivity failed: {e}")
    
    async def test_api_endpoints(self):
        """Test API endpoint accessibility and responses"""
        print("\n🌐 Testing API Endpoints")
        print("========================")
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        endpoints_to_test = [
            ("/health", "GET", False, "Application health check"),
            ("/health/db", "GET", False, "Database health check"),
            ("/api/v3/sitemap-files/", "GET", True, "Sitemap files listing"),
            ("/api/v3/dev-tools/scheduler_status", "GET", True, "Scheduler status"),
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint, method, auth_required, description in endpoints_to_test:
                try:
                    request_headers = headers if auth_required else {}
                    response = await client.request(method, f"{self.api_base}{endpoint}", headers=request_headers)
                    
                    if response.status_code < 400:
                        print(f"✅ {endpoint} ({method}) - {description}")
                        self.record_test("api_endpoints", f"{method}_{endpoint.replace('/', '_')}", "PASS", 
                                       f"Status: {response.status_code}")
                    else:
                        print(f"❌ {endpoint} ({method}) - Status: {response.status_code}")
                        self.record_test("api_endpoints", f"{method}_{endpoint.replace('/', '_')}", "FAIL", 
                                       f"Status: {response.status_code}")
                
                except Exception as e:
                    print(f"❌ {endpoint} ({method}) - Error: {e}")
                    self.record_test("api_endpoints", f"{method}_{endpoint.replace('/', '_')}", "FAIL", f"Error: {e}")
    
    async def test_sitemap_creation_flow(self):
        """Test sitemap file creation and basic processing flow"""
        print("\n📄 Testing Sitemap Creation Flow")
        print("================================")
        
        # First, create a test domain
        test_domain_id = str(uuid.uuid4())
        test_tenant_id = str(uuid.uuid4())
        
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            # Create test domain
            await conn.execute("""
                INSERT INTO domains (id, domain, status, tenant_id) 
                VALUES ($1, $2, $3, $4) 
                ON CONFLICT DO NOTHING
            """, test_domain_id, "test-component-example.com", "active", test_tenant_id)
            
            print("✅ Test domain created")
            self.record_test("sitemap_flow", "domain_creation", "PASS", "Test domain created successfully")
            
            await conn.close()
            
        except Exception as e:
            print(f"❌ Test domain creation failed: {e}")
            self.record_test("sitemap_flow", "domain_creation", "FAIL", f"Domain creation failed: {e}")
            return
        
        # Test sitemap file creation via API
        sitemap_data = {
            "domain_id": test_domain_id,
            "url": "https://test-component-example.com/sitemap.xml",
            "sitemap_type": "Standard",
            "discovery_method": "component_test"
        }
        
        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/api/v3/sitemap-files/",
                    json=sitemap_data,
                    headers=headers
                )
                
                if response.status_code == 201:
                    sitemap_response = response.json()
                    sitemap_file_id = sitemap_response.get("id")
                    print(f"✅ Sitemap file created: {sitemap_file_id}")
                    self.record_test("sitemap_flow", "api_creation", "PASS", f"Sitemap file ID: {sitemap_file_id}")
                    
                    # Test manual trigger
                    trigger_response = await client.post(
                        f"{self.api_base}/api/v3/dev-tools/trigger-sitemap-import/{sitemap_file_id}",
                        headers=headers
                    )
                    
                    if trigger_response.status_code == 200:
                        print("✅ Manual trigger executed")
                        self.record_test("sitemap_flow", "manual_trigger", "PASS", "Manual trigger successful")
                    else:
                        print(f"❌ Manual trigger failed: {trigger_response.status_code}")
                        self.record_test("sitemap_flow", "manual_trigger", "FAIL", 
                                       f"Status: {trigger_response.status_code}")
                    
                    # Clean up test data
                    await self.cleanup_test_data()
                    
                else:
                    print(f"❌ Sitemap file creation failed: {response.status_code}")
                    self.record_test("sitemap_flow", "api_creation", "FAIL", f"Status: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Sitemap creation flow failed: {e}")
            self.record_test("sitemap_flow", "api_creation", "FAIL", f"Error: {e}")
    
    async def cleanup_test_data(self):
        """Clean up test data created during component testing"""
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            # Clean up in reverse dependency order
            await conn.execute("DELETE FROM pages WHERE sitemap_file_id IN (SELECT id FROM sitemap_files WHERE discovery_method = 'component_test')")
            await conn.execute("DELETE FROM sitemap_files WHERE discovery_method = 'component_test'")
            await conn.execute("DELETE FROM domains WHERE domain LIKE 'test-component-%'")
            
            await conn.close()
            print("✅ Test data cleanup completed")
            self.record_test("cleanup", "test_data_removal", "PASS", "Test data cleaned up successfully")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
            self.record_test("cleanup", "test_data_removal", "FAIL", f"Cleanup failed: {e}")
    
    async def run_all_tests(self):
        """Run all component tests"""
        print("🧪 WF6 Component Testing Suite")
        print("==============================")
        
        await self.setup()
        await self.test_database_connectivity()
        await self.test_api_endpoints()
        await self.test_sitemap_creation_flow()
        
        # Generate summary
        print(f"\n📊 Test Summary")
        print("===============")
        print(f"Total Tests: {self.test_results['summary']['total']}")
        print(f"✅ Passed: {self.test_results['summary']['passed']}")
        print(f"❌ Failed: {self.test_results['summary']['failed']}")
        
        if self.test_results['summary']['total'] > 0:
            success_rate = (self.test_results['summary']['passed'] / self.test_results['summary']['total']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Save results
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / "wf6_component_test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")
        
        return self.test_results['summary']['failed'] == 0


async def main():
    """Main entry point"""
    tester = WF6ComponentTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All component tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some component tests failed. Check results for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
