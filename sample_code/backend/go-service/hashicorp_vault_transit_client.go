package main

import (
    "context"
    "fmt"

    vault "github.com/hashicorp/vault/api"
)

func encryptWithVaultTransit(ctx context.Context, address string, token string, keyName string, plaintext string) (map[string]any, error) {
    config := vault.DefaultConfig()
    config.Address = address

    client, err := vault.NewClient(config)
    if err != nil {
        return nil, err
    }
    client.SetToken(token)

    payload := map[string]any{
        "plaintext": plaintext,
        "context":   "customer-profile",
    }
    secret, err := client.Logical().Write("transit/encrypt/"+keyName, payload)
    if err != nil {
        return nil, err
    }
    fmt.Println("vault transit encrypt response received")
    return secret.Data, nil
}
