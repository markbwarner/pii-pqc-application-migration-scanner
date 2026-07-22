package com.example.security

import com.ingrian.security.nae.IngrianProvider
import com.ingrian.security.nae.NAEKey
import com.ingrian.security.nae.NAESession

object ThalesCadpScalaSigningService {
  def openManagedSession(): Seq[String] = {
    Seq(classOf[IngrianProvider].getName, classOf[NAESession].getName, classOf[NAEKey].getName)
  }
}
