"""
Database operations for the domains table.
"""
from datetime import datetime
from typing import Dict, Any
import json
from ..db.sb_connection import db

class DomainDBHandler:
    """Handles all database operations for the domains table."""
    
    @staticmethod
    async def insert_domain_data(domain_data: Dict[str, Any]) -> Dict[str, Any]:
        # Convert dict fields to JSON strings
        if isinstance(domain_data.get('tech_stack'), dict):
            domain_data['tech_stack'] = json.dumps(domain_data['tech_stack'])
        if isinstance(domain_data.get('meta_json'), dict):
            domain_data['meta_json'] = json.dumps(domain_data['meta_json'])
        """
        Insert new domain data into the domains table.
        
        Args:
            domain_data: Dictionary containing domain metadata
            
        Returns:
            Dict containing the inserted record
        """
        query = """
            INSERT INTO domains (
                tenant_id,
                domain,
                title,
                description,
                favicon_url,
                logo_url,
                language,
                is_wordpress,
                wordpress_version,
                has_elementor,
                email_addresses,
                phone_numbers,
                facebook_url,
                twitter_url,
                linkedin_url,
                instagram_url,
                youtube_url,
                tech_stack,
                content_scrape_status,
                content_scrape_at,
                first_scan,
                last_scan,
                meta_json
            ) VALUES (
                %(tenant_id)s,
                %(domain)s,
                %(title)s,
                %(description)s,
                %(favicon_url)s,
                %(logo_url)s,
                %(language)s,
                %(is_wordpress)s,
                %(wordpress_version)s,
                %(has_elementor)s,
                %(email_addresses)s,
                %(phone_numbers)s,
                %(facebook_url)s,
                %(twitter_url)s,
                %(linkedin_url)s,
                %(instagram_url)s,
                %(youtube_url)s,
                %(tech_stack)s,
                'complete',
                now(),
                now(),
                now(),
                %(meta_json)s
            )
            RETURNING *;
        """
        
        with db.get_cursor() as cur:
            try:
                cur.execute(query, domain_data)
                return cur.fetchone()
            except Exception as e:
                print(f"Error inserting domain data: {str(e)}")
                raise

    @staticmethod
    async def update_domain_data(domain: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing domain data.
        
        Args:
            domain: Domain to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Dict containing the updated record
        """
        # Build dynamic update query based on provided fields
        update_fields = []
        for key in update_data.keys():
            update_fields.append(f"{key} = %({key})s")
        
        update_fields.append("updated_at = now()")
        update_string = ", ".join(update_fields)
        
        query = f"""
            UPDATE domains 
            SET {update_string}
            WHERE domain = %(domain)s
            RETURNING *;
        """
        
        with db.get_cursor() as cur:
            try:
                params = {**update_data, "domain": domain}
                cur.execute(query, params)
                return cur.fetchone()
            except Exception as e:
                print(f"Error updating domain data: {str(e)}")
                raise

    @staticmethod
    async def get_domain_data(domain: str) -> Dict[str, Any]:
        """
        Retrieve domain data.
        
        Args:
            domain: Domain to retrieve
            
        Returns:
            Dict containing the domain record
        """
        query = """
            SELECT * FROM domains
            WHERE domain = %(domain)s;
        """
        
        with db.get_cursor() as cur:
            try:
                cur.execute(query, {"domain": domain})
                return cur.fetchone()
            except Exception as e:
                print(f"Error retrieving domain data: {str(e)}")
                raise
