#!/usr/bin/env python3
"""
MinIO Auto-Discovery Setup Script
================================

This script:
1. Automatically discovers folders in backend/raw_files/
2. Creates a bucket for each discovered folder
3. Creates a "testclient" bucket with all files organized by project
4. Uploads files from each folder to their respective buckets

Supported file types: PDF, TXT, MD, JSON, DOC, DOCX

Usage: python setup_minio.py
"""

import os
import time
from pathlib import Path
from minio import Minio
from minio.error import S3Error

def main():
    print("🚀 Setting up MinIO with auto-discovery...")
    
    # Configuration
    endpoint = "localhost:9000"
    access_key = "minioadmin"
    secret_key = "minioadmin"
    
    # Directory containing folders to discover
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    raw_files_dir = backend_dir / "raw_files"
    
    print(f"📋 Configuration:")
    print(f"   Endpoint: {endpoint}")
    print(f"   Source Directory: {raw_files_dir}")
    
    # Check if directory exists
    if not raw_files_dir.exists():
        print(f"❌ Directory not found: {raw_files_dir}")
        print("💡 Make sure the raw_files directory exists in backend/")
        return False
    
    # Discover folders in raw_files directory
    discovered_folders = []
    for item in raw_files_dir.iterdir():
        if item.is_dir():
            discovered_folders.append(item.name)
    
    if not discovered_folders:
        print(f"❌ No folders found in {raw_files_dir}")
        return False
    
    print(f"🔍 Discovered folders: {', '.join(discovered_folders)}")
    
    # Get supported file extensions
    supported_extensions = {'.pdf', '.txt', '.md', '.json', '.doc', '.docx'}
    
    # Count files in each folder
    folder_file_counts = {}
    total_files = 0
    
    for folder_name in discovered_folders:
        folder_path = raw_files_dir / folder_name
        files_in_folder = []
        
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                files_in_folder.append(file_path)
        
        folder_file_counts[folder_name] = len(files_in_folder)
        total_files += len(files_in_folder)
        
        print(f"   📁 {folder_name}: {len(files_in_folder)} files")
    
    if total_files == 0:
        print(f"❌ No supported files found in any folder")
        print(f"💡 Supported extensions: {', '.join(supported_extensions)}")
        return False
    
    print(f"📊 Total files to upload: {total_files}")
    print()
    
    try:
        # Create MinIO client
        client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        
        # Wait for MinIO to be ready
        print("⏳ Waiting for MinIO to be ready...")
        max_retries = 10
        for i in range(max_retries):
            try:
                client.list_buckets()
                print("✅ MinIO is ready!")
                break
            except Exception as e:
                if i == max_retries - 1:
                    print(f"❌ MinIO not ready after {max_retries} attempts: {e}")
                    print("💡 Make sure MinIO is running: docker-compose -f docker-compose.local.yml up -d")
                    return False
                print(f"   Attempt {i+1}/{max_retries}...")
                time.sleep(2)
        
        # Create only testclient bucket
        bucket_name = "testclient"
        
        print(f"📦 Creating bucket...")
        try:
            if client.bucket_exists(bucket_name):
                print(f"   ✅ Bucket '{bucket_name}' already exists")
            else:
                client.make_bucket(bucket_name)
                print(f"   ✅ Created bucket '{bucket_name}'")
        except Exception as e:
            print(f"   ❌ Failed to create bucket '{bucket_name}': {e}")
            return False
        
        # Upload all files to testclient bucket with project structure
        print(f"\n📤 Uploading files to testclient bucket with project structure...")
        
        total_uploaded = 0
        total_failed = 0
        for folder_name in discovered_folders:
            folder_path = raw_files_dir / folder_name
            print(f"   📁 Processing {folder_name} project...")
            
            for file_path in folder_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    # Create object name with project structure
                    relative_path = file_path.relative_to(raw_files_dir)
                    object_name = str(relative_path).replace('\\', '/')
                    
                    try:
                        client.fput_object(
                            bucket_name="testclient",
                            object_name=object_name,
                            file_path=str(file_path)
                        )
                        
                        print(f"      ✅ {object_name}")
                        total_uploaded += 1
                        
                    except Exception as e:
                        print(f"      ❌ Failed to upload {object_name}: {e}")
                        total_failed += 1
        
        print(f"   📊 testclient: {total_uploaded} uploaded, {total_failed} failed")
        
        # Summary
        print(f"\n📊 Upload Summary:")
        print(f"   ✅ Successfully uploaded: {total_uploaded} files")
        if total_failed > 0:
            print(f"   ❌ Failed uploads: {total_failed} files")
        
        # Verify the uploads
        print(f"\n🔍 Verifying uploads...")
        
        try:
            objects = list(client.list_objects("testclient", recursive=True))
            if objects:
                total_size = sum(obj.size for obj in objects)
                print(f"   📦 testclient: {len(objects)} files ({total_size:,} bytes)")
                
                # Group files by project
                projects = {}
                for obj in objects:
                    project = obj.object_name.split('/')[0]
                    if project not in projects:
                        projects[project] = []
                    projects[project].append(obj)
                
                for project, files in projects.items():
                    project_size = sum(f.size for f in files)
                    print(f"      📁 {project}/: {len(files)} files ({project_size:,} bytes)")
                    for f in files[:2]:
                        print(f"         📄 {f.object_name}")
                    if len(files) > 2:
                        print(f"         ... and {len(files) - 2} more files")
            else:
                print(f"   📦 testclient: empty")
        except Exception as e:
            print(f"   ❌ Error checking bucket testclient: {e}")
        
        print(f"\n🎯 Setup completed successfully!")
        print(f"   MinIO Console: http://localhost:9001")
        print(f"   Username: minioadmin")
        print(f"   Password: minioadmin")
        print(f"   Discovered projects: {', '.join(discovered_folders)}")
        print(f"   Created bucket: testclient")
        
        print(f"\n🚀 You can now test the GraphRAG pipeline with:")
        for folder in discovered_folders:
            print(f"""   curl -X POST "http://localhost:8000/api/workflow/graph_preprocessing" \\
     -H "Content-Type: application/json" \\
     -d '{{"input": {{"workflow_id": "test_{folder}", "client_id": "testclient", "project_id": "{folder}", "domain_id": "{folder}"}}}}'""")
        
        return total_uploaded > 0
        
    except S3Error as e:
        print(f"❌ MinIO error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)