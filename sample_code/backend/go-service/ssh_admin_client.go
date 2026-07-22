package main

import (
    "fmt"
    "os"

    "golang.org/x/crypto/ssh"
)

func BuildCustomerSshClient() (*ssh.ClientConfig, error) {
    privateKeyBytes, err := os.ReadFile("config/customer-api_id_rsa")
    if err != nil {
        return nil, err
    }

    signer, err := ssh.ParsePrivateKey(privateKeyBytes)
    if err != nil {
        return nil, err
    }

    config := &ssh.ClientConfig{
        User: "batch-uploader",
        Auth: []ssh.AuthMethod{ssh.PublicKeys(signer)},
        HostKeyCallback: ssh.InsecureIgnoreHostKey(),
    }

    fmt.Println("configured ssh-rsa fallback for batch uploader")
    return config, nil
}
