#!/usr/bin/env python3
"""
Pre-flight validation script for HuggingFace image generation
Run this before executing the blog generator to catch all potential errors
"""

import os
import sys
from pathlib import Path

def validate_environment():
    """Comprehensive validation of image generation setup"""
    
    print("=" * 70)
    print("🔍 PRE-FLIGHT CHECK: HuggingFace Image Generation")
    print("=" * 70)
    
    errors = []
    warnings = []
    
    # 1. Check .env file exists
    print("\n1️⃣ Checking .env file...")
    # Look for .env in the same directory as this script
    script_dir = Path(__file__).parent
    env_path = script_dir / ".env"
    if not env_path.exists():
        errors.append("❌ .env file not found in script directory")
        print(f"   ❌ NOT FOUND: {env_path.absolute()}")
    else:
        print(f"   ✅ FOUND: {env_path.absolute()}")
    
    # 2. Check API key
    print("\n2️⃣ Checking HUGGINGFACE_API_KEY...")
    from dotenv import load_dotenv
    load_dotenv(env_path)  # Load from script directory
    
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        errors.append("❌ HUGGINGFACE_API_KEY not set in .env file")
        print("   ❌ NOT SET")
    elif not api_key.startswith("hf_"):
        errors.append(f"❌ Invalid API key format. Should start with 'hf_' but got: {api_key[:10]}...")
        print(f"   ❌ INVALID FORMAT: {api_key[:10]}...")
    elif len(api_key) < 20:
        warnings.append(f"⚠️  API key seems too short ({len(api_key)} chars)")
        print(f"   ⚠️  KEY TOO SHORT: {len(api_key)} characters")
    else:
        print(f"   ✅ VALID: {api_key[:10]}...{api_key[-4:]} ({len(api_key)} chars)")
    
    # 3. Check required packages
    print("\n3️⃣ Checking Python packages...")
    required_packages = {
        'huggingface_hub': 'huggingface_hub',
        'PIL': 'Pillow',
        'dotenv': 'python-dotenv',
        'requests': 'requests',
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            errors.append(f"❌ Missing package: {package}")
            print(f"   ❌ {package} - Run: pip install {package}")
    
    # 4. Test HuggingFace client initialization
    print("\n4️⃣ Testing HuggingFace client initialization...")
    if api_key and api_key.startswith("hf_"):
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(token=api_key)
            print("   ✅ Client initialized successfully")
        except Exception as e:
            errors.append(f"❌ Failed to initialize HuggingFace client: {e}")
            print(f"   ❌ FAILED: {e}")
    else:
        warnings.append("⚠️  Skipping client test due to invalid API key")
        print("   ⚠️  SKIPPED (invalid API key)")
    
    # 5. Check image directory
    print("\n5️⃣ Checking images directory...")
    images_dir = script_dir / "images"
    if images_dir.exists():
        print(f"   ✅ EXISTS: {images_dir.absolute()}")
        # Count existing images
        existing_images = list(images_dir.glob("*.png"))
        if existing_images:
            print(f"   ℹ️  Found {len(existing_images)} existing images")
    else:
        print(f"   ℹ️  Will be created: {images_dir.absolute()}")
    
    # 6. Test PIL/Pillow
    print("\n6️⃣ Testing Pillow (PIL) functionality...")
    try:
        from PIL import Image
        from io import BytesIO
        # Create a test image
        test_img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        test_img.save(buffer, format='PNG')
        data = buffer.getvalue()
        if len(data) > 0:
            print(f"   ✅ Pillow working correctly ({len(data)} bytes test image)")
        else:
            errors.append("❌ Pillow produced empty image")
            print("   ❌ Test image is empty")
    except Exception as e:
        errors.append(f"❌ Pillow test failed: {e}")
        print(f"   ❌ FAILED: {e}")
    
    # 7. Check available models (quick test)
    print("\n7️⃣ Checking model availability...")
    if api_key and api_key.startswith("hf_"):
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(token=api_key)
            
            test_models = [
                "black-forest-labs/FLUX.1-schnell",
                "stabilityai/stable-diffusion-xl-base-1.0",
                "stabilityai/stable-diffusion-2-1",
            ]
            
            for model in test_models:
                try:
                    # Try to get model info (doesn't generate image)
                    print(f"   ℹ️  {model}...")
                except Exception as e:
                    if "gated" in str(e).lower():
                        warnings.append(f"⚠️  {model} is gated (may need approval)")
                        print(f"      ⚠️  GATED - May need approval")
                    elif "404" in str(e):
                        warnings.append(f"⚠️  {model} not found")
                        print(f"      ❌ NOT FOUND")
        except Exception as e:
            warnings.append(f"⚠️  Could not check models: {e}")
            print(f"   ⚠️  SKIPPED: {e}")
    else:
        print("   ⚠️  SKIPPED (invalid API key)")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    if errors:
        print(f"\n❌ CRITICAL ERRORS ({len(errors)}):")
        for error in errors:
            print(f"   {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")
    
    if not errors and not warnings:
        print("\n✅ ALL CHECKS PASSED!")
        print("   You're ready to generate images!")
    elif not errors:
        print("\n✅ READY WITH WARNINGS")
        print("   Image generation should work, but check warnings above")
    else:
        print("\n❌ NOT READY")
        print("   Fix the errors above before running image generation")
    
    print("=" * 70)
    
    return len(errors) == 0

if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)
