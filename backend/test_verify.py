from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hash = "$2b$12$dgs5eaLkh1bjNERXE74LyeETxdM2C3r3jdAEXbBqSPJkd81BPl1Tu"
print("Hash to verify:", hash)

# Let's see if passlib can verify it against some dummy passwords, but we don't know it.
# Instead, let's just create a new hash and verify it.
new_hash = pwd_context.hash("test1234")
print("New hash:", new_hash)
print("Verify:", pwd_context.verify("test1234", new_hash))
