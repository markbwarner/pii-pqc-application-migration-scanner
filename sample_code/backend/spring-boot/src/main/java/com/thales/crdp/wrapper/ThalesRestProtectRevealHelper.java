package com.thales.crdp.wrapper;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.io.IOException;

public class ThalesRestProtectRevealHelper extends ThalesProtectRevealHelper {

    private final String crdpHost;

    public ThalesRestProtectRevealHelper(String crdpHost, String metadata, String policyType, boolean showMetadata) {
        this.crdpHost = crdpHost;
        this.metadata = metadata;
        this.policyType = policyType;
        this.showMetadata = showMetadata;
    }

    @Override
    public String protectData(String plainText, String protectionPolicyName, String policyType) {
        if (!isValid(plainText)) {
            return plainText;
        }
        JsonObject payload = new JsonObject();
        payload.addProperty("protection_policy_name", protectionPolicyName);
        payload.addProperty("data", plainText);
        String responseBody = postJson("http://" + crdpHost + ":8090/v1/protect", payload.toString());
        JsonObject jsonObject = new Gson().fromJson(responseBody, JsonObject.class);
        String protectedData = jsonObject.get("protected_data").getAsString();
        if (policyType.equalsIgnoreCase("external") && jsonObject.has("external_version")) {
            this.metadata = jsonObject.get("external_version").getAsString();
            return protectedData;
        }
        this.metadata = protectedData.substring(0, 7);
        return showMetadata ? protectedData : parseProtectedValue(protectedData);
    }

    @Override
    public String revealData(String encryptedData, String protectionPolicyName, String policyType) {
        JsonObject payload = new JsonObject();
        payload.addProperty("protection_policy_name", protectionPolicyName);
        payload.addProperty("protected_data", encryptedData);
        payload.addProperty("username", revealUser);
        if (policyType.equalsIgnoreCase("external") && metadata != null) {
            payload.addProperty("external_version", metadata);
        }
        String responseBody = postJson("http://" + crdpHost + ":8090/v1/reveal", payload.toString());
        return new Gson().fromJson(responseBody, JsonObject.class).get("data").getAsString();
    }

    private String postJson(String url, String body) {
        OkHttpClient client = new OkHttpClient.Builder().build();
        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json"), body);
        Request request = new Request.Builder().url(url).post(requestBody).addHeader("Content-Type", "application/json").build();
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        } catch (IOException exception) {
            throw new RuntimeException("CRDP call failed", exception);
        }
    }
}
