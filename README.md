# 42Crunch API Security Testing Tutorial

## Introduction

This tutorial walks you through the process of testing an API using 42Crunch Audit and Scan tools. The workflow uses Github Actions services to start a sample vulnerable API within the workflow runner, minimizing setup steps, and then runs 42Crunch Audit and 42Crunch Scan against the API.

Audit and Scan results are made available in the SARIF format and uploaded to Github Code Scanning automatically.

## What is 42Crunch Audit?

Security Audit performs over 300 checks on your API contract, ranging from its structure and semantics to its security and input and output data definition. Security Audit reviews your API definition on three levels:

- Security: How good are the security definitions in your API? Have you defined authentication and authorization methods, and is your chosen protocol secure enough?
- Data definitions: What is the data definition quality of your API? How well have you defined what data your API accepts as input or can include in the output it produces, and how strong are the schemas you have defined for your API and its parameters?
- OpenAPI format: Is your API a valid and well-formed OpenAPI file, and does it follow the best practices and the spirit of the OpenAPI Specification? Can it be correctly parsed, reviewed, or protected?


## What is 42Crunch Scan?

42Crunch Scan is a dynamic API security scanner that can be used to test APIs for vulnerabilities. It leverages the API OpenAPI definition to automatically test the API for a number of issues, across authentication, authorization and improper input validation. 

42Crunch Scan also validates API responses to ensure that the API implementation conforms to its definition and does not leak additional data or stack traces for example.

The scan classifies vulnerabilities it finds according to the OWASP API Security Top 10. You can learn more about scan by watching [this short 5 mins video](https://42crunch.com/free-user-faq/).

## PhotoManager API

The API you will use is derived from an [original OWASP](https://github.com/DevSlop/Pixi) project, as part of the DevSlop workgroup. It is a vulnerable API which exposes many of the common API security issues, such as authorization deficiencies, lack of input validation or data leakage.

The repository contains a docker compose file you can use, should you want to run and test the API locally. The Postman collection to drive the API is available [here](https://www.postman.com/get-42crunch/workspace/42crunch-api/collection/13761657-2fe8d964-9687-4a95-9e16-2c06e7d5fe7e).

![](./graphics/photo_manager_postman.png)

## Prerequisites

**GitHub Code Scanning**: this task assumes that GitHub Advanced Security is enabled on your repository. Code scanning is available for all public repositories on GitHub.com. Code scanning is also available for private repositories owned by organizations that use GitHub Enterprise Cloud and have a license for GitHub Advanced Security. For more information, see [About GitHub Advanced Security](https://docs.github.com/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning#enabling-code-scanning-for-a-repository).)"

*Note*: this tutorial leverages the [Freemium version](https://github.com/marketplace/actions/42crunch-rest-api-dynamic-security-testing-freemium) of 42Crunch Scan. It is now available for GitHubActions and will be added on more CI/CD platforms in the future.

## Running the tutorial

In order to run this tutorial, you will need to fork this repository. To do this, click on the "Fork" button in the top right corner of this page.

### Enable workflows

Once you fork this repository, workflows will be disabled for security reasons. You need to enable workflows in order to run them. To do this, go to the "Actions" tab of your repository and click on the "I understand my workflows, go ahead and enable them" button.

![](./graphics/freemium_eval_enableWorkflows.png)

You can check  https://docs.github.com/en/actions/managing-workflow-runs/approving-workflow-runs-from-public-forks for further details.

### Run the workflows

Workflows will run automatically when you commit changes to the repository, on branches and PRs. You can also run them manually by clicking on the "Run workflow" button.

![](./graphics/run_workflow.png)

## View the results in Code Scanning

Once the workflows have completed, you can view the security testing results inside the Security tab of your repository, under Code Scanning Alerts. The full SARIF reports are also exported as an artifact.

![](./graphics/code_scanning_results.png)

## Viewing SARIF files in Visual Studio Code

Microsoft provides a [SARIF viewer extension](https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer) you can install into Visual Studio Code. Used in conjunction with [42Crunch extension](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi), it helps you view issues found by 42Crunch Audit within the OpenAPI file.

The SARIF extension, once connected to GitHub, can directly display the issues from GitHub Code Scanning.

![](./graphics/SARIFinVSCode.png)

## Understanding the audit workflow

The workflow is defined in the `.github/workflows/42c-audit.yaml` file. It is composed of 3 steps:
1. Checkout the code repository
2. Run 42Crunch Audit: the audit action finds all OpenAPI/Swagger files in the repository and runs the audit against them. The audit action also uploads the results to GitHub Code Scanning, if the `upload-to-code-scanning` parameter is set to true. Additionally, the audit action exports the results as PDF format, if the `export-as-pdf` parameter is provided.
3. Save the SARIF and PDF reports as an artifact

A full list of audit action parameters is available [here](https://github.com/marketplace/actions/42crunch-rest-api-static-security-testing-freemium).

```yaml
- name: Checkout repo
    uses: actions/checkout@v4
- name: Audit API definition for security issues
    uses: 42Crunch/api-security-audit-action-freemium@main
    with:
        # Upload results to Github Code Scanning
        # Set to false if you don't have Github Advanced Security.
        upload-to-code-scanning: true
        log-level: info
        sarif-report: 42Crunch_AuditReport_${{ github.run_id }}.SARIF
        export-as-pdf: 42Crunch_AuditReport_${{ github.run_id }}.pdf
        audit-reports-dir: ${{ github.workspace }}/reports
- name: save-sarif-report
    if: always()        
    uses: actions/upload-artifact@v3
    with:
        name: 42Crunch_AuditReport_${{ github.run_id }}
        path: 42Crunch_AuditReport_${{ github.run_id }}.SARIF
        if-no-files-found: error
```

## Understanding the scan workflow

The workflow is defined in the `.github/workflows/42crunch-api-security-scan.yml` file. It is composed of 4 steps:

1. Checkout the code repository
2. Retrieving the credential to be used by the scan at execution time. This is done by using the /login endpoint of the Pixi API. For testing simplicity, the user and password are set at the beginning of the workflow. In real scenarios, the user and password would be stored in Github Secrets.
3. Run 42Crunch Scan and upload the results to GitHub Code Scanning, using the credential retrieved in the previous step.
4. Save the SARIF report as an artifact

```yaml
      - name: Checkout repo
        uses: actions/checkout@v4
      ...  
      - name: get_photoapi_token
        id: get_photoapi_token
        run: |
          login_response=$(python .42c/scripts/pixi-login.py -u ${{ env.USER_NAME }} -p ${{ env.USER_PASS }} -t ${{ env.TARGET_URL }})
          echo "PHOTO_API_TOKEN=$login_response" >> $GITHUB_OUTPUT
      - name: Scan API for vulnerabilities
        uses: 42Crunch/api-security-scan-action-freemium@v1
        with:
            api-definition: api-specifications/PhotoManager.json
            api-credential: ${{ steps.get_photoapi_token.outputs.PHOTO_API_TOKEN }}
            target-url: "http://app:8090/api"
            upload-to-code-scanning: true
            scan-report: 42Crunch_RawReport_${{ github.run_id }}.json
            log-level: info
            sarif-report: 42Crunch_ScanReport_${{ github.run_id }}.SARIF
      - name: save-sarif-report
        if: always()        
        uses: actions/upload-artifact@v3
        with:
            name: 42Crunch_ScanReport_${{ github.run_id }}
            path: 42Crunch_ScanReport_${{ github.run_id }}.SARIF
            if-no-files-found: error
```

A full list of scan action parameters is available [here](https://github.com/marketplace/actions/42crunch-rest-api-dynamic-security-testing-freemium)

## Conclusion

In this tutorial, you have learnt how to use 42Crunch Scan to test an API for vulnerabilities leveraging the Freemium version of 42Crunch Scan.
