# tools/test_importlab.py
print("Testing importlab import...")
try:
    import importlab

    print("importlab imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
