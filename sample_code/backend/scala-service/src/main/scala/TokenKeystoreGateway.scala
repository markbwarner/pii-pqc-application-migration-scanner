package com.example.security

import io.jsonwebtoken.Jwts
import io.jsonwebtoken.SignatureAlgorithm
import java.io.FileInputStream
import java.security.KeyStore
import java.security.cert.X509Certificate

object TokenKeystoreGateway {
  def loadCertificateChain(path: String, password: Array[Char]): X509Certificate = {
    val keyStore = KeyStore.getInstance("PKCS12")
    val stream = new FileInputStream(path)
    keyStore.load(stream, password)
    keyStore.getCertificate("signing-cert").asInstanceOf[X509Certificate]
  }

  def buildToken(subject: String): String = {
    Jwts.builder()
      .setSubject(subject)
      .signWith(SignatureAlgorithm.RS256, "placeholder-private-key")
      .compact()
  }
}
