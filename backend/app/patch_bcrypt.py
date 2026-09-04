import bcrypt

# Monkeypatch bcrypt to automatically truncate passwords longer than 72 bytes.
# This prevents compatibility issues between passlib and newer bcrypt versions (4.x/5.x).
_original_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return _original_hashpw(password_bytes, salt)

bcrypt.hashpw = _patched_hashpw
