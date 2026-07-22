use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Header, Validation};
use openssl::ssl::{SslConnector, SslFiletype, SslMethod};
use openssl::x509::X509;
use ssh2::Session;
use std::net::TcpStream;

pub fn build_tls_connector(cert_pem: &[u8], key_path: &str) -> Result<SslConnector, openssl::error::ErrorStack> {
    let certificate = X509::from_pem(cert_pem)?;
    let mut builder = SslConnector::builder(SslMethod::tls())?;
    builder.set_certificate(&certificate)?;
    builder.set_private_key_file(key_path, SslFiletype::PEM)?;
    Ok(builder.build())
}

pub fn issue_rs256_token(claims_json: &str, private_key_pem: &[u8]) -> Result<String, jsonwebtoken::errors::Error> {
    let header = Header::new(Algorithm::RS256);
    encode(&header, &serde_json::json!({"claims": claims_json}), &EncodingKey::from_rsa_pem(private_key_pem)?)
}

pub fn validate_rs256_token(token: &str, public_key_pem: &[u8]) -> Result<(), jsonwebtoken::errors::Error> {
    let validation = Validation::new(Algorithm::RS256);
    let _ = decode::<serde_json::Value>(token, &DecodingKey::from_rsa_pem(public_key_pem)?, &validation)?;
    Ok(())
}

pub fn open_ssh_session(host: &str) -> Result<(), Box<dyn std::error::Error>> {
    let tcp = TcpStream::connect(host)?;
    let mut session = Session::new()?;
    session.set_tcp_stream(tcp);
    session.handshake()?;
    Ok(())
}
