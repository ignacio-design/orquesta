#!/usr/bin/env python3
"""
Script maestro: sincroniza HubSpot + envía emails
"""

import subprocess
import sys

def run_sync():
    """Sincroniza HubSpot"""
    print("\n🔄 Sincronizando con HubSpot...")
    result = subprocess.run([sys.executable, 'process_leads.py'], cwd='/Users/patocarrere/.openclaw/workspace')
    return result.returncode == 0

def send_emails():
    """Envía emails automáticos"""
    print("\n📧 Enviando emails automáticos...")
    result = subprocess.run([sys.executable, 'send_emails.py'], cwd='/Users/patocarrere/.openclaw/workspace')
    return result.returncode == 0

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 ORQUESTA - SINCRONIZACIÓN COMPLETA")
    print("=" * 60)
    
    sync_ok = run_sync()
    emails_ok = send_emails()
    
    print("\n" + "=" * 60)
    print(f"✅ HubSpot: {'OK' if sync_ok else 'ERROR'}")
    print(f"✅ Emails: {'OK' if emails_ok else 'ERROR'}")
    print("=" * 60)
