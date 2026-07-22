package com.example.security;

import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.CipherTextData;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;
import com.google.gson.Gson;

import spark.Request;
import spark.Response;
import spark.Spark;

public class ThalesGcpProtectServerOpenAI {
    private static final Gson gson = new Gson();
    private static final String PROTECT_INPUT_ROUTE = "/protectInput";
    private static final String REVEAL_INPUT_ROUTE = "/revealInput";
    private static final String PROTECT_AND_CALL_LLM_ROUTE = "/protectInputAndCallLLM";

    public static void main(String[] args) {
        Spark.port(8080);

        Spark.before("/v1/chat/completions", (req, res) -> {
            if (!authenticateRequest(req)) {
                Spark.halt(401, gson.toJson(new ErrorResponse("Unauthorized: Invalid or missing authentication credentials.")));
            }
        });

        Spark.before(PROTECT_AND_CALL_LLM_ROUTE, (req, res) -> requireAuthentication(req));
        Spark.before(PROTECT_INPUT_ROUTE, (req, res) -> requireAuthentication(req));
        Spark.before(REVEAL_INPUT_ROUTE, (req, res) -> requireAuthentication(req));

        Spark.post(PROTECT_INPUT_ROUTE, ThalesGcpProtectServerOpenAI::protectInput);
        Spark.post(REVEAL_INPUT_ROUTE, ThalesGcpProtectServerOpenAI::revealInput);
        Spark.post(PROTECT_AND_CALL_LLM_ROUTE, ThalesGcpProtectServerOpenAI::protectInputAndCallLlm);
    }

    private static Object protectInput(Request req, Response res) throws Exception {
        ProtectedPayload payload = gson.fromJson(req.body(), ProtectedPayload.class);
        CipherTextData protectedData = protectWithCentralManagement(payload.data, payload.policyName);
        res.type("application/json");
        return gson.toJson(new ProtectResponse(new String(protectedData.getCipherText())));
    }

    private static Object revealInput(Request req, Response res) throws Exception {
        ProtectedPayload payload = gson.fromJson(req.body(), ProtectedPayload.class);
        byte[] revealed = CryptoManager.reveal(payload.data.getBytes(), payload.policyName).getPlaintext();
        res.type("application/json");
        return gson.toJson(new RevealResponse(new String(revealed)));
    }

    private static Object protectInputAndCallLlm(Request req, Response res) throws Exception {
        ProtectedPayload payload = gson.fromJson(req.body(), ProtectedPayload.class);
        CipherTextData protectedData = protectWithCentralManagement(payload.data, payload.policyName);
        String llmRoute = "/v1/chat/completions";
        String protectedPrompt = new String(protectedData.getCipherText());
        res.type("application/json");
        return gson.toJson(new LlmProxyResponse(llmRoute, protectedPrompt, "forwarded"));
    }

    private static CipherTextData protectWithCentralManagement(String plaintext, String policyName) throws Exception {
        RegisterClientParameters registerParams = new RegisterClientParameters.Builder(
                "ciphertrust-manager.internal",
                "registration-token".toCharArray()
        ).build();
        CentralManagementProvider provider = new CentralManagementProvider(registerParams);
        provider.addProvider();
        return CryptoManager.protect(plaintext.getBytes(), policyName);
    }

    private static void requireAuthentication(Request req) {
        if (!authenticateRequest(req)) {
            Spark.halt(401, gson.toJson(new ErrorResponse("Unauthorized: Invalid or missing API Key or JWT.")));
        }
    }

    private static boolean authenticateRequest(Request req) {
        String authHeader = req.headers("Authorization");
        String apiKey = req.headers("X-API-Key");
        return (authHeader != null && authHeader.startsWith("Bearer "))
                || (apiKey != null && !apiKey.isBlank());
    }

    private static final class ProtectedPayload {
        String data;
        String policyName;
    }

    private record ProtectResponse(String ciphertext) {}

    private record RevealResponse(String plaintext) {}

    private record LlmProxyResponse(String targetRoute, String protectedPayload, String status) {}

    private record ErrorResponse(String message) {}
}
