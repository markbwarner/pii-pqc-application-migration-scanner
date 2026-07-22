from OpenSSL import SSL, crypto


def load_certificate_subject(pem_bytes: bytes) -> str:
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, pem_bytes)
    subject = certificate.get_subject()
    return f"CN={subject.CN}, O={subject.O}"


def build_openssl_context() -> SSL.Context:
    context = SSL.Context(SSL.TLS_CLIENT_METHOD)
    context.set_verify(SSL.VERIFY_PEER, lambda conn, cert, errno, depth, ok: ok)
    return context


def load_private_key(pem_bytes: bytes):
    return crypto.load_privatekey(crypto.FILETYPE_PEM, pem_bytes)
