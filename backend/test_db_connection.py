import os
import sys
import socket
import urllib.parse
from urllib.parse import urlparse

def test_connection():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get connection string from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return

    # Parse the connection string
    try:
        result = urlparse(db_url)
        username = result.username
        password = result.password
        hostname = result.hostname
        port = result.port or 5432  # Default PostgreSQL port
        database = result.path[1:]  # Remove leading '/'
        
        print(f"🔍 Testing connection to: {hostname}")
        
        # Test DNS resolution
        try:
            ip = socket.gethostbyname(hostname)
            print(f"✅ DNS Resolution: Success ({hostname} → {ip})")
        except socket.gaierror:
            print(f"❌ DNS Resolution: Failed to resolve {hostname}")
            print("   - Check your internet connection")
            print("   - Verify the hostname is correct")
            print("   - Try pinging the hostname manually")
            return
            
        # Test port connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        try:
            sock.connect((hostname, port))
            print(f"✅ Port {port}: Open")
        except (socket.timeout, ConnectionRefusedError) as e:
            print(f"❌ Port {port}: {str(e)}")
            print("   - The port might be blocked by a firewall")
            print("   - Check if your network allows outbound connections to this port")
            sock.close()
            return
        finally:
            sock.close()
            
        # Test database connection (if above tests pass)
        try:
            import psycopg2
            print("\n🔑 Attempting database connection...")
            conn = psycopg2.connect(
                dbname=database,
                user=username,
                password=password,
                host=hostname,
                port=port,
                connect_timeout=5
            )
            print("✅ Database Connection: Success!")
            
            # Test a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"📊 Database Version: {db_version[0]}")
            
            cursor.close()
            conn.close()
            
        except ImportError:
            print("❌ psycopg2 package not found. Install it with:")
            print("   pip install psycopg2-binary")
        except Exception as e:
            print(f"❌ Database Connection Failed: {str(e)}")
            print("\n🔧 Troubleshooting Steps:")
            print("1. Verify your username and password are correct")
            print("2. Check if your IP is whitelisted in Supabase")
            print("3. Ensure your Supabase project is active")
            print("4. Try using a different network/VPN")
            
    except Exception as e:
        print(f"❌ Error parsing connection string: {str(e)}")
        print("   - Check your DATABASE_URL format in .env file")
        print("   - It should look like: postgresql://user:password@host:port/dbname")

if __name__ == "__main__":
    test_connection()
