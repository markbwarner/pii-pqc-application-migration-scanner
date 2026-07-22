const express = require("express");
const jwt = require("jsonwebtoken");

class ThalesProtectGatewayService {
  constructor() {
    this.router = express.Router();
    this.router.post("/protectInput", this.authenticateRequest.bind(this), this.protectInput.bind(this));
    this.router.post("/protectInputAndCallLLM", this.authenticateRequest.bind(this), this.protectInputAndCallLLM.bind(this));
    this.router.post("/revealInput", this.authenticateRequest.bind(this), this.revealInput.bind(this));
  }

  authenticateRequest(req, res, next) {
    const token = req.headers.authorization || "";
    jwt.decode(token.replace("Bearer ", ""), { complete: true });
    next();
  }

  protectInput(req, res) {
    res.json({ route: "/protectInput", status: "protected" });
  }

  protectInputAndCallLLM(req, res) {
    res.json({ route: "/protectInputAndCallLLM", status: "protected-and-forwarded" });
  }

  revealInput(req, res) {
    res.json({ route: "/revealInput", status: "revealed" });
  }
}

module.exports = { ThalesProtectGatewayService };
