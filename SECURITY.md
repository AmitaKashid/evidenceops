# Security policy

EvidenceOps is a portfolio reference implementation and should not process production confidential data without a security review.

Please do not open public issues containing secrets, private documents, API keys, or exploit details. Report security concerns privately to the repository owner.

The default configuration uses a local deterministic provider and synthetic data. Remote model calls are disabled unless `ENABLE_REMOTE_MODEL=true` and approved credentials are configured.
