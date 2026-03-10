import hashlib

keys = ["admin-key", "query-key", "test-key", "key-1", "key-2", "secret", "password"]
for key in keys:
    h = hashlib.sha256(key.encode()).hexdigest()
    print(f"{key}: {h}")

# Also check the hashes from the file
hashes = [
    "246bb403d6082880ab88f8422b8540ff78b7ba0b2306157fa7022fefb3a4ecf7",
    "35cd23cc610c61fcd916f67d38579126fc26312d590fb51e18f837f074765110"
]
print("\nTarget Hashes:")
for target in hashes:
    print(target)
