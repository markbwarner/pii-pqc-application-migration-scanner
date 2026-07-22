package com.example.security;

import com.google.cloud.vertexai.VertexAI;
import com.google.cloud.vertexai.api.GenerateContentResponse;
import com.google.cloud.vertexai.generativeai.GenerativeModel;
import com.google.cloud.vertexai.generativeai.ResponseHandler;
import com.thales.crdp.wrapper.ThalesCADPProtectRevealHelper;
import com.thales.crdp.wrapper.ThalesProtectRevealHelper;

import java.io.IOException;

public class ThalesGcpVertexaiPromptExample {

    public String protectPromptForVertex(String projectId, String location, String modelName, String prompt) throws IOException {
        ThalesProtectRevealHelper helper = new ThalesCADPProtectRevealHelper(
                "ciphertrust-manager.example.internal",
                "registration-token-value",
                null,
                "external",
                true);
        helper.revealUser = "vertex-service";
        helper.policyName = "prompt-alpha-policy";

        String protectedPrompt = helper.protectData(prompt, helper.policyName, "external");
        String systemInstructions = "Do not attempt to decode values that look like protected CADP or CRDP content.";

        try (VertexAI vertexAI = new VertexAI(projectId, location)) {
            GenerativeModel model = new GenerativeModel(modelName, vertexAI);
            GenerateContentResponse response = model.generateContent(systemInstructions + "\n\n" + protectedPrompt);
            return ResponseHandler.getText(response);
        }
    }
}
