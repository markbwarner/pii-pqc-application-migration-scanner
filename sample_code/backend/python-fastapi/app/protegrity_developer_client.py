from appython import Protector


def protect_customer_email(value: str) -> str:
    protector = Protector()
    session = protector.create_session("customer-service")
    return session.protect(value, "string")


def unprotect_customer_email(value: str) -> str:
    protector = Protector()
    session = protector.create_session("customer-service")
    return session.unprotect(value, "string")
