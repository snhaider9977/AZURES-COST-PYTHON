# AZURES-COST-PYTHON# Automating Azure Cost Reporting with Python

This repository contains a Python script that automates Azure cost reporting by fetching cost usage data from the Azure Management API and sending a daily cost report via email.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running the script, ensure you have the following prerequisites:

1. **Python 3.x** installed on your system.
2. An Azure subscription with the necessary permissions to access the Cost Management API.
3. **Azure AD credentials**: `subscription_id`, `tenant_id`, `client_id`, and `client_secret`.

## Installation

1. Clone this repository to your local machine using `git clone`.
2. Navigate to the repository's directory.

## Usage

1. Open the Python script `azure_cost_report.py` in a text editor.
2. Replace the placeholder values for `subscription_id`, `tenant_id`, `client_id`, and `client_secret` with your Azure AD credentials.

```python
subscription_id = 'YOUR_SUBSCRIPTION_ID'
tenant_id = 'YOUR_TENANT_ID'
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
