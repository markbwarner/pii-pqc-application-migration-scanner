curl -u token-user:changeit https://VTS_IP_Address/vts/rest/v2.0/tokenize \
  -H "Content-Type: application/json" \
  -d '{"tokengroup":"FF1_Tok_Group","data":"4111111111111111","tokentemplate":"FF1_Tok_Template"}'

curl -u token-user:changeit https://VTS_IP_Address/vts/rest/v2.0/detokenize \
  -H "Content-Type: application/json" \
  -d '{"tokengroup":"FF1_Tok_Group","token":"EzchFFKH33EGhopWc|Bb|TV(","tokentemplate":"FF1_Tok_Template"}'
