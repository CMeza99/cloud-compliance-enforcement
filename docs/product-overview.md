# Compliance Enforcement

“Policy-As-Code”

## Executive Summary

Codifing policies provides documented policy of what is actually being enforced. Further more it enables collaboration, cost reduction, and improving the security posture.

"Policy As Code" enables the ability to enforce policy with automation.
It empowers stakeholders, such as SecOps and service teams, to be part of the policy creation process through submissions and peer-review.
As code, exceptions are automaticly documented as to why and when.
This provies a common set of policies across the organization. As well as, providing transparency to the process.

## Overview

### Users / Stakeholders

* System Engineers - those responsible for the infrastructure
* Security Engineers - those tasked with information security and compliance
* Account Owners - Department that pays the bill for the account

### Gains

* Cost reduction
* Increased security posture
* Policy enforcement
* Versioned and documented policies
* Auditble policies

### Minable Usable Product

* AWS only
* Leverage Cloud Custodian
* Find and Remove:
  * EBS Snapshot over year old
  * Unused AMIs over 30 days old
  * EC2 instances that have been stopped for over a year
* Process can be manual
  * Execution of tool
  * Change approval

## Long Term Vision

### The Tooling Platform

* Automated Executions
  * GitOps
  * Scheduled Runs
  * CloudWatch Triggers
    * Respond when resources are created
* Per Account Settings
  * Jinja Templeting
* Metrics
* C7n monitoring
  * Send c7n logs to CloudWatch
* Auditable - Send output to S3
* Notification / Alerting
  * Email
  * Slack
* Trusted Advisor Integration
* Multicloud
* Price impact
* Chef InSpec

### Compliance Enforcement Polcies

* EC2 Instance tags
* Excessive Uptime (implies patches are not applied)

## Glossary

* Policy-as-Code - maintaining policies in vcs in a text based format
* Asset - a cloud resource, i.e. an AWS EC2 instance