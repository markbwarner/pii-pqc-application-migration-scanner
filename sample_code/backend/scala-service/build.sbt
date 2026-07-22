name := "pqc-scala-service"

scalaVersion := "2.13.15"

libraryDependencies ++= Seq(
  "io.jsonwebtoken" % "jjwt-api" % "0.12.6",
  "org.bouncycastle" % "bcpkix-jdk18on" % "1.78.1"
)
