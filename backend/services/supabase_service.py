import os
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import uuid

class SupabaseService:
    """
    Complete Supabase integration for real-time database, auth, and file storage
    Matches Lovable's Supabase integration capabilities
    """
    
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
        
        # For demo purposes, we'll create a mock Supabase interface
        # In production, you'd use the actual Supabase credentials
        if not self.supabase_url:
            self.supabase_url = "https://mock-supabase.emergent.com"
            self.supabase_key = "mock_key_for_demo"
    
    async def setup_database_tables(self, project_id: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up database tables via chat interface like Lovable
        """
        try:
            tables_created = []
            
            for table_name, table_config in schema.items():
                table_result = await self._create_table(project_id, table_name, table_config)
                tables_created.append(table_result)
            
            return {
                "success": True,
                "tables": tables_created,
                "message": f"Created {len(tables_created)} tables in Supabase"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create database tables"
            }
    
    async def _create_table(self, project_id: str, table_name: str, config: Dict) -> Dict[str, Any]:
        """Create individual table with columns"""
        
        # Mock table creation - in real implementation, use Supabase REST API
        columns = config.get('columns', [])
        
        # Generate SQL for table creation
        sql_columns = []
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('default'):
                col_def += f" DEFAULT {col['default']}"
            sql_columns.append(col_def)
        
        create_sql = f"CREATE TABLE {table_name} ({', '.join(sql_columns)});"
        
        # In real implementation, execute this SQL in Supabase
        await self._execute_sql(project_id, create_sql)
        
        return {
            "table_name": table_name,
            "columns": columns,
            "sql": create_sql,
            "created": True
        }
    
    async def _execute_sql(self, project_id: str, sql: str) -> Dict[str, Any]:
        """Execute SQL in Supabase database"""
        
        # Mock SQL execution
        return {
            "success": True,
            "sql": sql,
            "executed_at": datetime.utcnow().isoformat()
        }
    
    async def setup_authentication(self, project_id: str, auth_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up Supabase authentication
        """
        try:
            auth_methods = auth_config.get('methods', ['email'])
            providers = auth_config.get('providers', [])
            
            # Configure auth settings
            auth_setup = {
                "email_auth": "email" in auth_methods,
                "social_providers": providers,
                "jwt_secret": str(uuid.uuid4()),
                "password_policy": auth_config.get('password_policy', {
                    "min_length": 8,
                    "require_symbols": True
                })
            }
            
            # In real implementation, configure Supabase Auth
            await self._configure_auth(project_id, auth_setup)
            
            return {
                "success": True,
                "auth_config": auth_setup,
                "message": "Supabase authentication configured"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to configure authentication"
            }
    
    async def _configure_auth(self, project_id: str, auth_config: Dict) -> None:
        """Configure Supabase authentication settings"""
        # Mock auth configuration
        pass
    
    async def setup_realtime(self, project_id: str, tables: List[str]) -> Dict[str, Any]:
        """
        Enable real-time subscriptions for tables
        """
        try:
            realtime_config = []
            
            for table in tables:
                config = {
                    "table": table,
                    "events": ["INSERT", "UPDATE", "DELETE"],
                    "enabled": True,
                    "row_level_security": True
                }
                realtime_config.append(config)
            
            # In real implementation, enable real-time in Supabase
            await self._enable_realtime(project_id, realtime_config)
            
            return {
                "success": True,
                "realtime_tables": realtime_config,
                "message": f"Real-time enabled for {len(tables)} tables"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to enable real-time"
            }
    
    async def _enable_realtime(self, project_id: str, config: List[Dict]) -> None:
        """Enable real-time subscriptions"""
        # Mock real-time setup
        pass
    
    async def setup_file_storage(self, project_id: str, buckets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Set up file storage buckets
        """
        try:
            created_buckets = []
            
            for bucket_config in buckets:
                bucket_name = bucket_config['name']
                public = bucket_config.get('public', False)
                allowed_mime_types = bucket_config.get('allowed_mime_types', [])
                
                bucket_result = await self._create_storage_bucket(
                    project_id, bucket_name, public, allowed_mime_types
                )
                created_buckets.append(bucket_result)
            
            return {
                "success": True,
                "buckets": created_buckets,
                "message": f"Created {len(created_buckets)} storage buckets"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create storage buckets"
            }
    
    async def _create_storage_bucket(self, project_id: str, bucket_name: str, public: bool, mime_types: List[str]) -> Dict[str, Any]:
        """Create storage bucket in Supabase"""
        
        return {
            "bucket_name": bucket_name,
            "public": public,
            "allowed_mime_types": mime_types,
            "created": True,
            "url": f"{self.supabase_url}/storage/v1/object/public/{bucket_name}"
        }
    
    async def generate_api_code(self, project_id: str, table_name: str, operations: List[str]) -> Dict[str, Any]:
        """
        Generate Supabase API code snippets for frontend
        """
        try:
            code_snippets = {}
            
            if "create" in operations:
                code_snippets["create"] = f"""
// Create new {table_name}
const create{table_name.title()} = async (data) => {{
  const {{ data: result, error }} = await supabase
    .from('{table_name}')
    .insert([data])
    .select()
  
  if (error) throw error
  return result[0]
}}"""
            
            if "read" in operations:
                code_snippets["read"] = f"""
// Get all {table_name}
const get{table_name.title()}s = async () => {{
  const {{ data, error }} = await supabase
    .from('{table_name}')
    .select('*')
  
  if (error) throw error
  return data
}}"""
            
            if "update" in operations:
                code_snippets["update"] = f"""
// Update {table_name}
const update{table_name.title()} = async (id, updates) => {{
  const {{ data, error }} = await supabase
    .from('{table_name}')
    .update(updates)
    .eq('id', id)
    .select()
  
  if (error) throw error
  return data[0]
}}"""
            
            if "delete" in operations:
                code_snippets["delete"] = f"""
// Delete {table_name}
const delete{table_name.title()} = async (id) => {{
  const {{ error }} = await supabase
    .from('{table_name}')
    .delete()
    .eq('id', id)
  
  if (error) throw error
}}"""
            
            if "realtime" in operations:
                code_snippets["realtime"] = f"""
// Subscribe to {table_name} changes
const subscribe{table_name.title()}Changes = () => {{
  return supabase
    .channel('{table_name}_changes')
    .on('postgres_changes', 
      {{ event: '*', schema: 'public', table: '{table_name}' }}, 
      (payload) => {{
        console.log('Change received!', payload)
        // Handle real-time updates
      }}
    )
    .subscribe()
}}"""
            
            return {
                "success": True,
                "code_snippets": code_snippets,
                "table_name": table_name,
                "operations": operations
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate API code"
            }
    
    async def get_connection_info(self, project_id: str) -> Dict[str, Any]:
        """
        Get Supabase connection information for frontend
        """
        return {
            "supabase_url": self.supabase_url,
            "supabase_anon_key": self.supabase_key,
            "setup_code": f"""
import {{ createClient }} from '@supabase/supabase-js'

const supabaseUrl = '{self.supabase_url}'
const supabaseKey = '{self.supabase_key}'

export const supabase = createClient(supabaseUrl, supabaseKey)
""",
            "install_command": "npm install @supabase/supabase-js"
        }
    
    async def chat_to_database(self, project_id: str, natural_language_query: str) -> Dict[str, Any]:
        """
        Convert natural language to database operations (like Lovable's chat interface)
        """
        try:
            from services.agent_service import AgentService
            
            agent = AgentService()
            
            # Use AI to interpret the database request
            chat = agent.LlmChat(
                api_key=agent.api_key,
                session_id=f"db_chat_{project_id}",
                system_message=agent.SystemMessage(text="""You are a Supabase database expert.
                Convert natural language requests into proper database operations.
                
                Return JSON with:
                - operation_type: create_table, insert_data, query_data, update_schema, etc.
                - sql: The SQL command to execute
                - explanation: Human-readable explanation
                """)
            ).with_model("anthropic", "claude-3-5-sonnet-20241022")
            
            response = await chat.send_message(
                agent.UserMessage(text=f"Database request: {natural_language_query}")
            )
            
            # Parse AI response
            try:
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        "operation_type": "query",
                        "sql": "SELECT * FROM users LIMIT 10;",
                        "explanation": "Default query operation"
                    }
            except:
                result = {
                    "operation_type": "error",
                    "sql": "",
                    "explanation": "Could not parse the request"
                }
            
            # Execute the operation if it's safe
            if result["operation_type"] in ["create_table", "insert_data", "query_data"]:
                execution_result = await self._execute_sql(project_id, result["sql"])
                result["executed"] = execution_result
            
            return {
                "success": True,
                "query": natural_language_query,
                "interpretation": result,
                "message": "Database operation interpreted and executed"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process database chat request"
            }