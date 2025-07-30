# Cryptography Documentation

## Overview & Installation

The `cryptography` library is a comprehensive package designed to expose cryptographic primitives and recipes to Python developers. It provides a high-level interface for common cryptographic tasks while also offering low-level primitives for advanced use cases.

### Key Features
- **High-Level Recipes**: Simple interfaces for common cryptographic tasks
- **Low-Level Primitives**: Direct access to cryptographic algorithms
- **X.509 Certificate Support**: Complete certificate generation and validation
- **Symmetric Encryption**: AES, ChaCha20, and other block/stream ciphers
- **Asymmetric Encryption**: RSA, Elliptic Curve, and Diffie-Hellman
- **Digital Signatures**: RSA, DSA, ECDSA, and EdDSA signatures
- **Hashing**: SHA-1, SHA-2, SHA-3, BLAKE2, and other hash functions
- **Key Derivation**: PBKDF2, scrypt, Argon2, and HKDF
- **TLS/SSL Support**: Primitives for secure network communications
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Installation

**Standard Installation:**
```bash
pip install cryptography
```

**Version Check:**
```python
import cryptography
print(cryptography.__version__)
```

## Core Concepts & Architecture

### High-Level vs Low-Level APIs

**High-Level Recipes (Recommended for most users):**
- **Fernet**: Symmetric encryption with authentication
- **X.509**: Certificate and key management
- **Hazmat**: "Hazardous Materials" - low-level primitives

**Low-Level Primitives:**
- Direct algorithm implementations
- More flexibility but requires cryptographic knowledge
- Located in `cryptography.hazmat.primitives`

### Cryptographic Primitives

1. **Symmetric Encryption**: Same key for encryption and decryption
2. **Asymmetric Encryption**: Public/private key pairs
3. **Digital Signatures**: Authentication and integrity verification
4. **Hashing**: One-way functions for data integrity
5. **Key Derivation**: Generate keys from passwords or other keys

## Common Usage Patterns

### 1. High-Level Symmetric Encryption (Fernet)

**Basic Fernet Encryption:**
```python
from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()
print(f"Key: {key}")  # Keep this secret!

# Create a Fernet instance
fernet = Fernet(key)

# Encrypt data
message = b"Secret message"
encrypted = fernet.encrypt(message)
print(f"Encrypted: {encrypted}")

# Decrypt data
decrypted = fernet.decrypt(encrypted)
print(f"Decrypted: {decrypted}")  # b"Secret message"
```

**Fernet with Time-Based Tokens:**
```python
import time
from cryptography.fernet import Fernet

fernet = Fernet(Fernet.generate_key())

# Encrypt with timestamp
token = fernet.encrypt(b"time-sensitive data")

# Decrypt with TTL (time-to-live)
try:
    # Token valid for 30 seconds
    decrypted = fernet.decrypt(token, ttl=30)
    print("Token is valid:", decrypted)
except Exception as e:
    print("Token expired or invalid:", e)

# Simulate time passing
time.sleep(35)
try:
    decrypted = fernet.decrypt(token, ttl=30)
except Exception as e:
    print("Token expired:", e)
```

**Multiple Key Support:**
```python
from cryptography.fernet import Fernet, MultiFernet

# Generate multiple keys for key rotation
key1 = Fernet.generate_key()
key2 = Fernet.generate_key()

# Create MultiFernet with multiple keys
multi_fernet = MultiFernet([
    Fernet(key1),
    Fernet(key2)
])

# Encrypt (uses first key)
encrypted = multi_fernet.encrypt(b"data")

# Decrypt (tries all keys)
decrypted = multi_fernet.decrypt(encrypted)
print(decrypted)
```

### 2. Hashing and Message Digests

**Basic Hashing:**
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hashes import Hash

# SHA-256 hashing
digest = Hash(hashes.SHA256())
digest.update(b"Hello, ")
digest.update(b"World!")
hash_value = digest.finalize()

print(f"SHA-256: {hash_value.hex()}")
```

**Available Hash Algorithms:**
```python
from cryptography.hazmat.primitives import hashes

# Different hash algorithms
algorithms = [
    hashes.SHA1(),      # Deprecated for new applications
    hashes.SHA224(),
    hashes.SHA256(),    # Recommended
    hashes.SHA384(),
    hashes.SHA512(),
    hashes.SHA3_256(),
    hashes.SHA3_512(),
    hashes.BLAKE2b(64), # High performance
    hashes.BLAKE2s(32)
]

message = b"Test message"
for algo in algorithms:
    digest = Hash(algo)
    digest.update(message)
    result = digest.finalize()
    print(f"{algo.name}: {result.hex()[:16]}...")
```

**HMAC (Hash-based Message Authentication Code):**
```python
from cryptography.hazmat.primitives import hashes, hmac
import os

# Generate secret key
secret_key = os.urandom(32)
message = b"Important message"

# Create HMAC
h = hmac.HMAC(secret_key, hashes.SHA256())
h.update(message)
signature = h.finalize()

# Verify HMAC
h_verify = hmac.HMAC(secret_key, hashes.SHA256())
h_verify.update(message)
try:
    h_verify.verify(signature)
    print("HMAC verification successful")
except Exception as e:
    print("HMAC verification failed:", e)
```

### 3. Asymmetric Encryption (RSA)

**RSA Key Generation:**
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Get the public key
public_key = private_key.public_key()

# Serialize private key
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b"password123")
)

# Serialize public key
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print("Private key (encrypted):")
print(private_pem.decode())
print("\nPublic key:")
print(public_pem.decode())
```

**RSA Encryption and Decryption:**
```python
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Generate keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Encrypt with public key
message = b"Secret message for RSA encryption"
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print(f"Ciphertext: {ciphertext.hex()[:50]}...")

# Decrypt with private key
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print(f"Decrypted: {plaintext}")
```

### 4. Digital Signatures

**RSA Signatures:**
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Message to sign
message = b"Document to be signed"

# Create signature
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

print(f"Signature: {signature.hex()[:50]}...")

# Verify signature
try:
    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signature verification successful")
except Exception as e:
    print("Signature verification failed:", e)
```

**Elliptic Curve Signatures (ECDSA):**
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

# Generate EC private key
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Sign message
message = b"Message to sign with ECDSA"
signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))

print(f"ECDSA Signature: {signature.hex()[:50]}...")

# Verify signature
try:
    public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
    print("ECDSA signature verification successful")
except Exception as e:
    print("ECDSA signature verification failed:", e)
```

### 5. Symmetric Encryption (AES)

**AES GCM Mode (Authenticated Encryption):**
```python
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_aes_gcm(key, plaintext, associated_data):
    """Encrypt using AES-GCM with authentication."""
    # Generate random IV
    iv = os.urandom(12)  # 96-bit IV for GCM
    
    # Create cipher
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv)
    ).encryptor()
    
    # Add associated data (authenticated but not encrypted)
    encryptor.authenticate_additional_data(associated_data)
    
    # Encrypt
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    
    return iv, ciphertext, encryptor.tag

def decrypt_aes_gcm(key, associated_data, iv, ciphertext, tag):
    """Decrypt using AES-GCM with authentication."""
    # Create cipher with tag for verification
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag)
    ).decryptor()
    
    # Add associated data
    decryptor.authenticate_additional_data(associated_data)
    
    # Decrypt and verify
    return decryptor.update(ciphertext) + decryptor.finalize()

# Example usage
key = os.urandom(32)  # 256-bit key
message = b"Secret message with AES-GCM"
associated_data = b"public metadata"

# Encrypt
iv, ciphertext, tag = encrypt_aes_gcm(key, message, associated_data)
print(f"IV: {iv.hex()}")
print(f"Ciphertext: {ciphertext.hex()}")
print(f"Tag: {tag.hex()}")

# Decrypt
decrypted = decrypt_aes_gcm(key, associated_data, iv, ciphertext, tag)
print(f"Decrypted: {decrypted}")
```

**AES CBC Mode:**
```python
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def encrypt_aes_cbc(key, plaintext):
    """Encrypt using AES-CBC with PKCS7 padding."""
    # Generate random IV
    iv = os.urandom(16)  # 128-bit IV for CBC
    
    # Add padding
    padder = padding.PKCS7(128).padder()  # 128-bit block size
    padded_data = padder.update(plaintext) + padder.finalize()
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return iv, ciphertext

def decrypt_aes_cbc(key, iv, ciphertext):
    """Decrypt using AES-CBC and remove padding."""
    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext

# Example usage
key = os.urandom(32)  # 256-bit key
message = b"Message for AES-CBC encryption"

iv, ciphertext = encrypt_aes_cbc(key, message)
decrypted = decrypt_aes_cbc(key, iv, ciphertext)

print(f"Original: {message}")
print(f"Decrypted: {decrypted}")
```

### 6. Key Derivation Functions

**PBKDF2 (Password-Based Key Derivation):**
```python
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key_from_password(password: bytes, salt: bytes = None) -> tuple:
    """Derive encryption key from password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 32 bytes = 256 bits
        salt=salt,
        iterations=100000,  # OWASP recommended minimum
    )
    
    key = kdf.derive(password)
    return key, salt

# Example usage
password = b"user_password_123"
key, salt = derive_key_from_password(password)

print(f"Derived key: {key.hex()}")
print(f"Salt: {salt.hex()}")

# Verify derivation (for login scenarios)
kdf_verify = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)

try:
    kdf_verify.verify(password, key)
    print("Password verification successful")
except Exception as e:
    print("Password verification failed:", e)
```

**Scrypt (Memory-Hard KDF):**
```python
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def derive_key_scrypt(password: bytes, salt: bytes = None) -> tuple:
    """Derive key using Scrypt (memory-hard function)."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = Scrypt(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        n=2**14,    # CPU/memory cost factor
        r=8,        # Block size
        p=1,        # Parallelization factor
    )
    
    key = kdf.derive(password)
    return key, salt

# Example usage
password = b"secure_password"
key, salt = derive_key_scrypt(password)
print(f"Scrypt key: {key.hex()}")
```

**HKDF (HMAC-based Extract-and-Expand KDF):**
```python
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

def derive_multiple_keys(master_key: bytes, info: bytes, length: int = 32):
    """Derive multiple keys from a master key using HKDF."""
    salt = os.urandom(16)  # Optional but recommended
    
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info,
    )
    
    return hkdf.derive(master_key)

# Example: Derive different keys for different purposes
master_key = os.urandom(32)

encryption_key = derive_multiple_keys(master_key, b"encryption", 32)
mac_key = derive_multiple_keys(master_key, b"authentication", 32)
signing_key = derive_multiple_keys(master_key, b"signing", 32)

print(f"Encryption key: {encryption_key.hex()[:20]}...")
print(f"MAC key: {mac_key.hex()[:20]}...")
print(f"Signing key: {signing_key.hex()[:20]}...")
```

## Best Practices & Security

### 1. Key Management

**Secure Key Generation:**
```python
import os
import secrets
from cryptography.fernet import Fernet

class SecureKeyManager:
    """Secure key management practices."""
    
    @staticmethod
    def generate_secure_key(length: int = 32) -> bytes:
        """Generate cryptographically secure random key."""
        return secrets.token_bytes(length)
    
    @staticmethod
    def generate_fernet_key() -> bytes:
        """Generate Fernet key."""
        return Fernet.generate_key()
    
    @staticmethod
    def key_from_password(password: str, salt: bytes = None) -> tuple:
        """Derive key from password securely."""
        if salt is None:
            salt = os.urandom(16)
        
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Adjust based on security requirements
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt

# Usage
key_manager = SecureKeyManager()
secure_key = key_manager.generate_secure_key()
fernet_key = key_manager.generate_fernet_key()
derived_key, salt = key_manager.key_from_password("user_password")
```

### 2. Safe Algorithm Choices

**Recommended Algorithms:**
```python
# ✅ RECOMMENDED ALGORITHMS

# Symmetric Encryption
# - AES-256-GCM (authenticated encryption)
# - ChaCha20-Poly1305 (authenticated encryption)

# Asymmetric Encryption
# - RSA with 2048+ bit keys
# - Elliptic Curve (P-256, P-384, P-521)

# Hashing
# - SHA-256, SHA-384, SHA-512
# - BLAKE2b, BLAKE2s (high performance)

# Digital Signatures
# - RSA-PSS with SHA-256+
# - ECDSA with P-256+ curves
# - EdDSA (Ed25519, Ed448)

# ❌ AVOID THESE ALGORITHMS
# - SHA-1 (cryptographically broken)
# - MD5 (cryptographically broken)
# - RSA with < 2048 bit keys
# - DSA with < 2048 bit keys
```

### 3. Error Handling

**Comprehensive Error Handling:**
```python
from cryptography.exceptions import InvalidSignature, InvalidKey
from cryptography.fernet import InvalidToken
import logging

logger = logging.getLogger(__name__)

class CryptoHandler:
    """Safe cryptographic operations with error handling."""
    
    def __init__(self, key: bytes):
        try:
            self.fernet = Fernet(key)
        except Exception as e:
            logger.error(f"Invalid key provided: {e}")
            raise ValueError("Invalid encryption key")
    
    def encrypt_safe(self, data: bytes) -> bytes:
        """Safely encrypt data with error handling."""
        try:
            return self.fernet.encrypt(data)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise RuntimeError("Encryption operation failed")
    
    def decrypt_safe(self, token: bytes, ttl: int = None) -> bytes:
        """Safely decrypt data with error handling."""
        try:
            return self.fernet.decrypt(token, ttl=ttl)
        except InvalidToken:
            logger.warning("Invalid or expired token")
            raise ValueError("Token is invalid or expired")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise RuntimeError("Decryption operation failed")
    
    def verify_signature_safe(self, public_key, signature: bytes, 
                            message: bytes) -> bool:
        """Safely verify digital signature."""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            logger.warning("Invalid signature detected")
            return False
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException, Depends
from cryptography.fernet import Fernet
import os
import base64

app = FastAPI()

# Initialize encryption
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

class EncryptionService:
    def __init__(self):
        self.fernet = fernet
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data and return base64 encoded result."""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data and return string."""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid encrypted data")

encryption_service = EncryptionService()

@app.post("/encrypt")
async def encrypt_endpoint(data: str):
    try:
        encrypted = encryption_service.encrypt_data(data)
        return {"encrypted": encrypted}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Encryption failed")

@app.post("/decrypt")
async def decrypt_endpoint(encrypted_data: str):
    try:
        decrypted = encryption_service.decrypt_data(encrypted_data)
        return {"decrypted": decrypted}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Decryption failed")
```

### Password Hashing Service
```python
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import base64

class PasswordService:
    """Secure password hashing and verification service."""
    
    def __init__(self, iterations: int = 100000):
        self.iterations = iterations
    
    def hash_password(self, password: str) -> dict:
        """Hash password with salt using PBKDF2."""
        # Generate random salt
        salt = os.urandom(16)
        
        # Create KDF
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
        )
        
        # Derive key
        key = kdf.derive(password.encode('utf-8'))
        
        return {
            'hash': base64.b64encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8'),
            'iterations': self.iterations
        }
    
    def verify_password(self, password: str, stored_hash: str, 
                       stored_salt: str, iterations: int = None) -> bool:
        """Verify password against stored hash."""
        try:
            # Decode stored values
            salt = base64.b64decode(stored_salt.encode('utf-8'))
            expected_key = base64.b64decode(stored_hash.encode('utf-8'))
            
            # Use stored iterations if provided
            if iterations is None:
                iterations = self.iterations
            
            # Create KDF with same parameters
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
            )
            
            # Verify password
            kdf.verify(password.encode('utf-8'), expected_key)
            return True
            
        except Exception:
            return False

# Usage example
password_service = PasswordService()

# Hash a password
user_password = "secure_user_password_123"
password_data = password_service.hash_password(user_password)
print(f"Hash: {password_data['hash'][:20]}...")
print(f"Salt: {password_data['salt'][:20]}...")

# Verify password
is_valid = password_service.verify_password(
    user_password,
    password_data['hash'],
    password_data['salt'],
    password_data['iterations']
)
print(f"Password valid: {is_valid}")
```

### Certificate and Key Management
```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import ipaddress

class CertificateManager:
    """X.509 certificate generation and management."""
    
    def generate_key_pair(self, key_size: int = 2048) -> tuple:
        """Generate RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def create_self_signed_cert(self, private_key, subject_name: str,
                               dns_names: list = None, 
                               ip_addresses: list = None,
                               days_valid: int = 365) -> x509.Certificate:
        """Create self-signed certificate."""
        # Subject and issuer (same for self-signed)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
        ])
        
        # Build certificate
        builder = x509.CertificateBuilder()
        
        # Basic certificate info
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(issuer)
        builder = builder.public_key(private_key.public_key())
        builder = builder.serial_number(x509.random_serial_number())
        
        # Validity period
        now = datetime.datetime.utcnow()
        builder = builder.not_valid_before(now)
        builder = builder.not_valid_after(now + datetime.timedelta(days=days_valid))
        
        # Subject Alternative Names
        san_list = []
        if dns_names:
            san_list.extend([x509.DNSName(name) for name in dns_names])
        if ip_addresses:
            san_list.extend([x509.IPAddress(ipaddress.ip_address(ip)) 
                           for ip in ip_addresses])
        
        if san_list:
            builder = builder.add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False
            )
        
        # Sign certificate
        certificate = builder.sign(private_key, hashes.SHA256())
        return certificate
    
    def save_key_and_cert(self, private_key, certificate, 
                         key_path: str, cert_path: str, password: bytes = None):
        """Save private key and certificate to files."""
        # Determine encryption for private key
        if password:
            encryption = serialization.BestAvailableEncryption(password)
        else:
            encryption = serialization.NoEncryption()
        
        # Save private key
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption,
            ))
        
        # Save certificate
        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

# Usage example
cert_manager = CertificateManager()

# Generate key pair
private_key, public_key = cert_manager.generate_key_pair()

# Create self-signed certificate
certificate = cert_manager.create_self_signed_cert(
    private_key,
    "example.com",
    dns_names=["example.com", "www.example.com"],
    ip_addresses=["192.168.1.1"],
    days_valid=365
)

# Save to files
cert_manager.save_key_and_cert(
    private_key,
    certificate,
    "private_key.pem",
    "certificate.pem",
    password=b"key_password"
)

print("Certificate and key generated successfully!")
```

## Troubleshooting & FAQs

### Common Issues

1. **Import Errors**
   ```python
   # Check if cryptography is properly installed
   try:
       import cryptography
       print(f"Cryptography version: {cryptography.__version__}")
   except ImportError:
       print("Install cryptography: pip install cryptography")
   ```

2. **Key Format Issues**
   ```python
   # Loading keys from different formats
   from cryptography.hazmat.primitives import serialization
   
   # Load PEM private key
   with open("private_key.pem", "rb") as key_file:
       private_key = serialization.load_pem_private_key(
           key_file.read(),
           password=b"password",  # None if no password
       )
   
   # Load DER private key
   with open("private_key.der", "rb") as key_file:
       private_key = serialization.load_der_private_key(
           key_file.read(),
           password=None,
       )
   ```

3. **Padding and Mode Issues**
   ```python
   # Correct RSA padding for different use cases
   from cryptography.hazmat.primitives.asymmetric import padding
   from cryptography.hazmat.primitives import hashes
   
   # For encryption (OAEP recommended)
   encrypted = public_key.encrypt(
       message,
       padding.OAEP(
           mgf=padding.MGF1(algorithm=hashes.SHA256()),
           algorithm=hashes.SHA256(),
           label=None
       )
   )
   
   # For signatures (PSS recommended)
   signature = private_key.sign(
       message,
       padding.PSS(
           mgf=padding.MGF1(hashes.SHA256()),
           salt_length=padding.PSS.MAX_LENGTH
       ),
       hashes.SHA256()
   )
   ```

### Performance Tips

1. **Key Reuse**: Generate keys once and reuse them
2. **Algorithm Choice**: Use AES-GCM for authenticated encryption
3. **Key Derivation**: Cache derived keys when possible
4. **Batch Operations**: Process multiple items together when possible

### Security Checklist

- ✅ Use authenticated encryption (AES-GCM, ChaCha20-Poly1305)
- ✅ Generate cryptographically secure random keys
- ✅ Use appropriate key sizes (AES-256, RSA-2048+, EC-P256+)
- ✅ Implement proper key derivation for passwords
- ✅ Handle exceptions securely (no information leakage)
- ✅ Use constant-time comparisons for sensitive data
- ✅ Keep private keys encrypted when stored
- ✅ Validate all inputs and parameters

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Available but not extensively used
- **Potential Use Cases**: API key encryption, certificate management, secure data storage
- **Benefits**: Industry-standard cryptographic primitives, comprehensive feature set

### Recommended ScraperSky Integration

```python
# ScraperSky encryption service
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class ScraperSkyEncryption:
    """Encryption service for ScraperSky sensitive data."""
    
    def __init__(self):
        # Load encryption key from environment
        key_b64 = os.environ.get('SCRAPERSKY_ENCRYPTION_KEY')
        if key_b64:
            self.key = base64.urlsafe_b64decode(key_b64.encode())
        else:
            # Generate new key (save this to environment)
            self.key = Fernet.generate_key()
            print(f"Generated new key: {base64.urlsafe_b64encode(self.key).decode()}")
        
        self.fernet = Fernet(self.key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage."""
        encrypted = self.fernet.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use."""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {e}")
    
    def hash_password(self, password: str, salt: bytes = None) -> dict:
        """Hash user password securely."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        
        return {
            'hash': base64.b64encode(key).decode(),
            'salt': base64.b64encode(salt).decode()
        }
    
    def verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """Verify user password."""
        try:
            salt = base64.b64decode(stored_salt.encode())
            expected_key = base64.b64decode(stored_hash.encode())
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            kdf.verify(password.encode(), expected_key)
            return True
        except Exception:
            return False

# Usage in ScraperSky
encryption_service = ScraperSkyEncryption()

# Encrypt sensitive API keys before storing in database
scraper_api_key = "your-scraper-api-key"
encrypted_key = encryption_service.encrypt_api_key(scraper_api_key)

# Store encrypted_key in database...

# Later, decrypt for use
decrypted_key = encryption_service.decrypt_api_key(encrypted_key)

# Hash user passwords securely
password_data = encryption_service.hash_password("user_password")
# Store password_data in database...

# Verify passwords during login
is_valid = encryption_service.verify_password(
    "user_password",
    password_data['hash'],
    password_data['salt']
)
```

### Integration with ScraperSky Features
1. **API Key Protection**: Encrypt ScraperAPI keys, Google Maps API keys
2. **User Authentication**: Secure password hashing and verification
3. **Data Encryption**: Encrypt sensitive scraped data before storage
4. **Certificate Management**: Generate certificates for HTTPS scraping
5. **Token Security**: Secure JWT token signing and verification

This documentation provides comprehensive guidance for working with the cryptography library, emphasizing security best practices and integration possibilities for the ScraperSky project.