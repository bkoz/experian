# experian

### Prerequisites
- Linux or Mac
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Experian Developer Credentials](https://developer.experian.com/)
- Copy `dot_env` to `.env` and edit as necessary


### Example Experian clients

Only this example is currently working.

```bash
uv run src/01-experian-business.py
```

```console
INFO:root:Obtained Experian access token.
INFO:root:{
    "requestId": "rrt-02dce8480b81b09df-c-ea-1454121-44360798-1",
    "success": true,
    "results": {
        "bin": "796744203",
        "businessName": "EXPERIAN INFORMATION SOLUTIONS, INC",
        "address": {
            "street": "475 ANTON BLVD",
            "city": "COSTA MESA",
            "state": "CA",
            "zip": "92626",
            "zipExtension": "7037"
        },
        "phone": "+17148307000",
        "taxId": "133015410",
        "websiteUrl": "http://www.experian.com",
        "legalBusinessName": "EXPERIAN INFORMATION SOLUTIONS, INC.",
        "dbaNames": null,
        "customerDisputeIndicator": false
    }
}
```