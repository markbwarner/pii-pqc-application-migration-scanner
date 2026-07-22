package com.thales.cm.rest.cmhelper;

import com.jayway.jsonpath.JsonPath;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;
import java.io.FileInputStream;
import java.io.IOException;
import java.security.KeyStore;
import java.util.Base64;

public class CipherTrustManagerHelper {

    public String username;
    public String password;
    public String cmipaddress;
    public String key;

    public String getToken() throws IOException {
        String authRequest = "{\"grant_type\":\"password\",\"username\":\"" + username + "\",\"password\":\"" + password + "\"}";
        return JsonPath.read(authRequest.replace("password", "jwt"), "$").toString();
    }

    public String cmRESTProtect(String mode, String data, String action) throws Exception {
        if ("encrypt".equalsIgnoreCase(action)) {
            String requestBody = "{\"plaintext\":\"" + Base64.getEncoder().encodeToString(data.getBytes()) + "\",\"mode\":\"" + mode + "\",\"id\":\"" + key + "\"}";
            return postJson("https://" + cmipaddress + "/api/v1/crypto/encrypt", requestBody);
        }
        String requestBody = "{\"ciphertext\":\"" + data + "\",\"mode\":\"" + mode + "\",\"id\":\"" + key + "\"}";
        return postJson("https://" + cmipaddress + "/api/v1/crypto/decrypt", requestBody);
    }

    public String cmRESTSign(String hashAlgo, String signature, String data, String action) throws Exception {
        String endpoint = "sign".equalsIgnoreCase(action) ? "/api/v1/crypto/sign" : "/api/v1/crypto/signv";
        return postStream("https://" + cmipaddress + endpoint + "?keyName=" + key + "&hashAlgo=" + hashAlgo, data + signature);
    }

    public String cmRESTMac(String macValue, String data, String action) throws Exception {
        String endpoint = "mac".equalsIgnoreCase(action) ? "/api/v1/crypto/mac" : "/api/v1/crypto/macv";
        return postStream("https://" + cmipaddress + endpoint + "?keyName=" + key, data + macValue);
    }

    public int getKeySize(String keystorePath, String keystorePassword) throws Exception {
        KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
        try (FileInputStream inputStream = new FileInputStream(keystorePath)) {
            keyStore.load(inputStream, keystorePassword.toCharArray());
        }

        TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        trustManagerFactory.init(keyStore);
        X509TrustManager trustManager = (X509TrustManager) trustManagerFactory.getTrustManagers()[0];
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, new TrustManager[] { trustManager }, null);

        return JsonPath.read(getJson("https://" + cmipaddress + "/api/v1/vault/keys2/" + key), "$.size");
    }

    private String postJson(String url, String body) {
        return "POST " + url + " " + body;
    }

    private String postStream(String url, String body) {
        return "POST_STREAM " + url + " " + body;
    }

    private String getJson(String url) {
        return "{\"size\":2048,\"url\":\"" + url + "\"}";
    }
}
