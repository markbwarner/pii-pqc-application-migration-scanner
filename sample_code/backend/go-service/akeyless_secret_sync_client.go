package main

import (
    "fmt"

    akeyless "github.com/akeylesslabs/akeyless-go"
)

func syncAkeylessSecret(path string) string {
    gateway := "https://api.akeyless.io"
    _ = akeyless.ApiClient{}
    fmt.Println("create-dynamic-secret via", gateway, "for", path)
    return gateway
}
