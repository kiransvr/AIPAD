# UAT Readiness Checklist

Use this checklist before sending the build to the client for UAT.

## 1. Build and CI

- [ ] GitHub Actions workflow is green on latest main commit.
- [ ] Required status checks are enforced on main:
  - CI / Backend Tests
  - CI / Frontend Build and Tests
- [ ] Release candidate is tagged (for example `uat-v1.0.0-rc1`).

## 2. Environment and Configuration

- [ ] Frontend uses environment-driven API base URL (`VITE_API_BASE_URL`).
- [ ] Backend secrets are provided from environment and not hardcoded.
- [ ] Production/staging `ALLOWED_HOSTS` and `CORS_ORIGINS` are configured.
- [ ] Rate limiting is enabled with expected values for UAT.

## 3. Security and Reliability

- [ ] Security headers are verified in staging responses.
- [ ] Standardized backend error envelope is verified (`error` + `request_id`).
- [ ] Error and access logs are accessible during UAT.
- [ ] Rollback plan is documented (app version + database rollback notes).

## 4. Functional Smoke Tests

- [ ] Sign in with each role (admin, risk, branch manager, loan officer).
- [ ] Upload valid portfolio file completes successfully.
- [ ] Upload invalid file shows row-level validation errors.
- [ ] PAR/NPL summary pages load correctly.
- [ ] Regional map and branch/officer views load correctly.

## 5. UAT Package to Client

- [ ] UAT URL shared.
- [ ] Test accounts shared by role.
- [ ] UAT scope and acceptance criteria shared.
- [ ] Known issues and workarounds shared.
- [ ] Support contact and turnaround SLA shared.

## Go/No-Go Decision

- [ ] GO for client UAT
- [ ] NO-GO (list blockers)

### Blockers

- 
