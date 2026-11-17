import os
from dotenv import load_dotenv
from cryptography import x509
import ssl

load_dotenv()
host = os.getenv("NEO4J_URI").split("://")[1].split("/")[0].split(":")[0]

# Only reads the certificate to see who issued it. It does not send your data.
pem = ssl.get_server_certificate((host, 7687))
cert = x509.load_pem_x509_certificate(pem.encode())

print("Certificate for:", cert.subject.rfc4514_string())
print("Issued by:      ", cert.issuer.rfc4514_string())