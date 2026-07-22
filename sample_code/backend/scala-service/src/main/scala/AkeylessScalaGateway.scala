package com.example.security

import io.akeyless.client.ApiClient
import io.akeyless.client.Configuration

object AkeylessScalaGateway {
  def managedOperations(): Seq[String] = {
    val api = new ApiClient()
    Configuration.setDefaultApiClient(api)
    val host = "https://api.akeyless.io"
    Seq(host, "create-dynamic-secret", "rotate-key", "verify-pkcs1")
  }
}
