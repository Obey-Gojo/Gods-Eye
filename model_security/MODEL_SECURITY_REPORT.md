# GodsEye - Model Security Report

## 1. Objective

The objective of the Model Security module is to ensure that the AI model used by GodsEye is authentic, has not been tampered with, behaves consistently under controlled input changes, and does not show an obvious behavioral signal associated with a Trojan/backdoor.

---

## 2. Role

**Team Role:** Member 3 - Model Security

The main responsibilities were:

- Model integrity verification
- SHA-256 model hashing
- Tamper detection
- Model behavior and robustness testing
- Anomaly screening
- Controlled backdoor/Trojan behavioral screening
- Generation of an overall model security score

---

## 3. Model Information

**Model:** YOLO11n  
**Model Version:** 1.0  
**Model File:** yolo11n.pt

### Trusted SHA-256 Hash

```text
0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1