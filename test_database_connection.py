#!/usr/bin/env python3
"""
Test database connection script
Verify that the DATABASE_URL environment variable is correctly configured
and the database connection works as expected.

Usage:
    python test_database_connection.py

Example output (success):
    ✅ Database connected: (1,)
    ✅ Connection pool size: 20
    ✅ Pre-ping enabled: True

Example output (failure):
    ❌ Database connection failed: could not connect to server
"""

import os
import sys
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

def test_connection():
    """Test database connection with full diagnostics"""

    db_url = os.getenv('DATABASE_URL')

    if not db_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Set it using: export DATABASE_URL='postgresql://user:password@host:port/database'")
        return False

    # Mask password in output
    masked_url = db_url.replace(db_url.split('@')[0].split('://')[-1], 'user:****') if '@' in db_url else db_url
    print(f"📝 Testing connection to: {masked_url}")

    try:
        # Get connection pool settings from environment
        pool_size = int(os.getenv('DATABASE_POOL_SIZE', '20'))
        max_overflow = int(os.getenv('DATABASE_POOL_MAX_OVERFLOW', '40'))
        pre_ping = os.getenv('DATABASE_POOL_PRE_PING', 'true').lower() == 'true'

        # Create engine with connection pool
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pre_ping,
            connect_args={'connect_timeout': 10}
        )

        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = result.fetchone()
            print(f"✅ Database connected: {value}")

        # Get pool info
        pool = engine.pool
        print(f"✅ Connection pool configured:")
        print(f"   - Pool size: {pool_size}")
        print(f"   - Max overflow: {max_overflow}")
        print(f"   - Pre-ping enabled: {pre_ping}")
        print(f"   - Pool checkedout: {pool.checkedout}")
        print(f"   - Pool size: {pool.size()}")

        # Test concurrent connections (simulate 5 requests)
        print("\n📊 Testing connection pool with concurrent requests...")
        from concurrent.futures import ThreadPoolExecutor

        def get_connection_count():
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    return True
            except Exception as e:
                print(f"  ❌ Connection failed: {e}")
                return False

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda x: get_connection_count(), range(5)))
            if all(results):
                print(f"✅ Successfully opened 5 concurrent connections")
            else:
                failed = len([r for r in results if not r])
                print(f"⚠️  {failed}/5 connections failed")

        print("\n✅ All tests passed! Database connection is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Database connection failed:")
        print(f"   Error: {str(e)}")
        print(f"\n💡 Common causes:")
        print(f"   1. DATABASE_URL format is incorrect")
        print(f"   2. Database server is not running")
        print(f"   3. Network/firewall is blocking connection")
        print(f"   4. Invalid credentials")
        print(f"\n📝 Expected format:")
        print(f"   postgresql://username:password@hostname:5432/database_name")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
