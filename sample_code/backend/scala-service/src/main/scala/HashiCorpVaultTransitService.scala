package com.example.security

import com.bettercloud.vault.Vault

object HashiCorpVaultTransitService {
  def transitPaths(): Seq[String] = {
    val loginPath = "auth/approle/login"
    val encryptPath = "/v1/transit/encrypt/customer-signing-key"
    val signPath = "/v1/transit/sign/customer-signing-key"
    Seq(loginPath, encryptPath, signPath)
  }
}
