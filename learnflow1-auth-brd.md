# LearnFlow — Authentication & Account Access

**Epic:** AUTH — Registration, Login, Session (JWT), Password Reset
**Prepared by:** Business Analysis, LearnFlow LMS
**Stack context:** FastAPI · React 19 · PostgreSQL 17 · JWT
**Status:** Draft for review

---

## 1. User Stories

### 1.1 Registration

**US-AUTH-01 — Self-service registration**
As a **prospective learner**, I want to **create a LearnFlow account with my email address and a password**, so that **I can enrol in courses under my own identity**.

**US-AUTH-02 — Email verification**
As a **new user**, I want to **confirm ownership of my email address before my account is fully active**, so that **nobody can register courses or receive notifications using an address that isn't mine**.

**US-AUTH-03 — Duplicate account prevention**
As a **returning user who has forgotten I already signed up**, I want to **be told when an address is already registered and be offered a route to sign in or reset my password**, so that **I don't create a second account and lose my learning history**.

### 1.2 Login

**US-AUTH-04 — Credential login**
As a **registered learner**, I want to **sign in with my email and password**, so that **I can reach my dashboard, enrolled courses and progress**.

**US-AUTH-05 — Protection against credential attacks**
As a **platform owner**, I want **repeated failed sign-in attempts to be throttled and the account temporarily locked**, so that **learner accounts are not compromised by brute-force or credential-stuffing attacks**.

**US-AUTH-06 — Post-login destination**
As a **learner who followed a deep link to a course page**, I want to **land back on that page after signing in**, so that **I don't lose my place and have to navigate again**.

### 1.3 Session & JWT Issuing

**US-AUTH-07 — Token issuance**
As a **signed-in learner**, I want **the platform to issue me a session credential on successful login**, so that **I can move between LearnFlow pages and API calls without re-entering my password**.

**US-AUTH-08 — Silent session renewal**
As a **learner working through a long lesson**, I want **my session to renew in the background**, so that **I am not signed out mid-assessment and lose unsaved work**.

**US-AUTH-09 — Sign out**
As a **learner using a shared or public computer**, I want to **sign out and have my session invalidated server-side**, so that **the next person on that machine cannot resume my session**.

**US-AUTH-10 — Role-aware access**
As a **platform owner**, I want **each issued token to carry the user's role and account status**, so that **learner, instructor and admin capabilities are enforced consistently across the API**.

### 1.4 Password Reset

**US-AUTH-11 — Request a reset**
As a **learner who has forgotten my password**, I want to **request a reset link by email**, so that **I can regain access without contacting support**.

**US-AUTH-12 — Complete a reset**
As a **learner holding a valid reset link**, I want to **set a new password and be told it worked**, so that **I can sign in again immediately**.

**US-AUTH-13 — Reset link safety**
As a **security stakeholder**, I want **reset links to be single-use, short-lived, and to invalidate existing sessions on use**, so that **a leaked or intercepted link has minimal exploitable value**.

**US-AUTH-14 — Change password while signed in**
As a **signed-in learner**, I want to **change my password by confirming my current one**, so that **I can rotate credentials without going through the email flow**.

---

## 2. Acceptance Criteria

### US-AUTH-01 — Self-service registration

- **Given** I am an unauthenticated visitor on the registration page
  **When** I submit a well-formed email, a password meeting policy, and a matching confirmation
  **Then** an account is created with status `pending_verification`, my password is stored only as a salted hash, and I am shown a "check your email" confirmation screen.

- **Given** I am on the registration page
  **When** I submit a password shorter than 10 characters or one appearing on the common-password deny list
  **Then** the account is not created and the specific policy rule I failed is shown inline against the password field.

- **Given** I am on the registration page
  **When** I submit an email that fails format validation
  **Then** the form is rejected client-side and server-side, and no record is written to the database.

- **Given** registration succeeds
  **When** the response is returned
  **Then** no session token is issued and the response body contains no password, hash, or internal user identifier.

### US-AUTH-02 — Email verification

- **Given** my account is `pending_verification`
  **When** I open the verification link within its 24-hour validity window
  **Then** my status changes to `active`, the token is consumed, and I am redirected to the sign-in page with a success message.

- **Given** I hold a verification link
  **When** I open it after 24 hours or open it a second time
  **Then** verification is refused with an explanatory message and an option to request a new link.

- **Given** my account is `pending_verification`
  **When** I attempt to sign in
  **Then** sign-in is refused with a message explaining verification is outstanding, and a resend option is offered (maximum 3 resends per hour).

### US-AUTH-03 — Duplicate account prevention

- **Given** an active account already exists for `x@example.com`
  **When** I submit a registration for that same address
  **Then** the API returns the same generic success response as a new registration, no second record is created, and the address owner receives an email stating a registration was attempted with links to sign in or reset.

- **Given** two registration requests for the same address arrive concurrently
  **When** both reach the database
  **Then** the unique constraint on the normalised email column ensures exactly one account row exists.

### US-AUTH-04 — Credential login

- **Given** I have an active, verified account
  **When** I submit my correct email and password
  **Then** I am authenticated, issued a session credential (see US-AUTH-07), and redirected to my dashboard.

- **Given** I have an active account
  **When** I submit an incorrect password, or an email that is not registered
  **Then** the response is an identical generic failure message in both cases, returned with comparable response timing, and the failed attempt is recorded.

- **Given** my account is suspended or deactivated
  **When** I submit correct credentials
  **Then** sign-in is refused with a message directing me to support, and no token is issued.

- **Given** I sign in successfully
  **When** the account record is updated
  **Then** the failed-attempt counter resets to zero and last-login timestamp and source IP are recorded.

### US-AUTH-05 — Protection against credential attacks

- **Given** I have made 5 consecutive failed sign-in attempts on one account
  **When** I make a sixth attempt
  **Then** the account is locked for 15 minutes, further attempts are refused regardless of credential correctness, and a security notification email is sent to the account owner.

- **Given** an account is locked
  **When** the 15-minute window elapses
  **Then** the lock clears automatically and the counter resets, without administrator intervention.

- **Given** a single IP address exceeds 20 sign-in attempts per minute across any accounts
  **When** the next request arrives
  **Then** it is rejected at the rate-limit layer with HTTP 429 and a `Retry-After` header.

### US-AUTH-06 — Post-login destination

- **Given** I request a protected URL while unauthenticated
  **When** I am redirected to sign in and then authenticate successfully
  **Then** I am returned to the originally requested URL.

- **Given** a return path is supplied
  **When** it points to an external host or is not a relative LearnFlow path
  **Then** it is discarded and I am sent to the default dashboard.

### US-AUTH-07 — Token issuance

- **Given** authentication succeeds
  **When** tokens are issued
  **Then** an access token with a 15-minute lifetime is returned to the client and a refresh token with a 7-day lifetime is set as an `HttpOnly`, `Secure`, `SameSite=Strict` cookie.

- **Given** an access token is issued
  **When** its payload is inspected
  **Then** it contains subject, role, issued-at, expiry, issuer and a unique token ID, and contains no email address, password hash or other sensitive attribute.

- **Given** a request carries an expired, malformed, or incorrectly signed token
  **When** it reaches a protected endpoint
  **Then** the API returns HTTP 401 and no business logic executes.

- **Given** a request carries a valid token whose role lacks the required permission
  **When** it reaches a protected endpoint
  **Then** the API returns HTTP 403 and the attempt is logged.

### US-AUTH-08 — Silent session renewal

- **Given** my access token has expired and my refresh token is still valid
  **When** the client calls the refresh endpoint
  **Then** a new access token is issued, the refresh token is rotated, and the previous refresh token is invalidated.

- **Given** a refresh token that has already been rotated is presented again
  **When** it reaches the refresh endpoint
  **Then** the request is refused, the entire token family for that user is revoked, and a security event is raised for review.

- **Given** my refresh token has expired
  **When** the client attempts renewal
  **Then** renewal is refused and I am returned to the sign-in page with my in-progress work preserved client-side where technically possible.

### US-AUTH-09 — Sign out

- **Given** I am signed in
  **When** I select sign out
  **Then** the refresh token is revoked server-side, the cookie is cleared, and client-side session state is discarded.

- **Given** I have signed out
  **When** an access token from that session is replayed before its natural expiry
  **Then** it is rejected because its token ID appears on the revocation list.

- **Given** I am signed in on multiple devices
  **When** I choose "sign out everywhere"
  **Then** all refresh tokens for my account are revoked.

### US-AUTH-10 — Role-aware access

- **Given** a user holds the `learner` role
  **When** they call an instructor- or admin-only endpoint
  **Then** the request is refused with HTTP 403.

- **Given** an administrator changes a user's role
  **When** that user's next token refresh occurs
  **Then** the newly issued token carries the updated role.

### US-AUTH-11 — Request a reset

- **Given** I am on the forgotten-password page
  **When** I submit any syntactically valid email address
  **Then** I always see the same neutral confirmation message, whether or not an account exists.

- **Given** an account exists for the submitted address
  **When** the request is processed
  **Then** a single-use reset token is generated, only its hash is persisted with a 30-minute expiry, and the email is dispatched within 60 seconds.

- **Given** I request a reset repeatedly
  **When** I exceed 3 requests per address per hour
  **Then** further requests are silently throttled with no additional emails sent.

- **Given** an account exists and a previous unused reset token is outstanding
  **When** a new reset is requested
  **Then** the earlier token is invalidated.

### US-AUTH-12 — Complete a reset

- **Given** I hold a valid, unexpired, unused reset token
  **When** I submit a new password meeting policy
  **Then** the password hash is replaced, the token is marked used, and I am redirected to sign in with a success message.

- **Given** I hold a reset token
  **When** it is expired, already used, or does not match a stored hash
  **Then** the reset is refused with a message offering to start the flow again, and no indication is given as to which condition failed.

- **Given** I complete a reset
  **When** the new password is saved
  **Then** a confirmation email is sent to the account address.

- **Given** my account was locked under US-AUTH-05
  **When** I complete a successful password reset
  **Then** the lock is cleared and the failed-attempt counter resets.

### US-AUTH-13 — Reset link safety

- **Given** a reset token is issued
  **When** the database is inspected
  **Then** only a hash of the token is stored; the plaintext value exists solely in the email.

- **Given** a password reset completes successfully
  **When** the change is committed
  **Then** all refresh tokens for that account are revoked and all other active sessions terminate.

- **Given** a reset token is generated
  **When** its entropy is assessed
  **Then** it is drawn from a cryptographically secure source with at least 128 bits of entropy.

### US-AUTH-14 — Change password while signed in

- **Given** I am signed in
  **When** I submit my correct current password and a compliant new password
  **Then** the password is updated, a confirmation email is sent, and my current session remains valid while all other sessions are revoked.

- **Given** I am signed in
  **When** I submit an incorrect current password
  **Then** the change is refused and the attempt counts toward the lockout threshold.

- **Given** I am signed in
  **When** I submit a new password identical to my current one
  **Then** the change is refused with an explanatory message.

---

## 3. Business Requirements Document — Section 4: Authentication & Account Access

### 4.1 Purpose

This section defines the business requirements for account creation and access control on LearnFlow. Authentication is the entry point to every other platform capability: enrolment, progress tracking, assessment and certification all depend on a reliable, attributable user identity. Without it, LearnFlow cannot personalise content, evidence course completion, or protect learner data.

### 4.2 Business Objectives

| Ref | Objective | Measure of success |
|-----|-----------|--------------------|
| BO-1 | Enable self-service account creation without administrator involvement | ≥ 95% of new accounts created without a support ticket |
| BO-2 | Establish a trustworthy identity for every learner record | 100% of active accounts have a verified email address |
| BO-3 | Minimise access-related support load | Password-reset tickets < 2% of monthly active users |
| BO-4 | Protect learner accounts and personal data | Zero credential-related security incidents per quarter |
| BO-5 | Keep sessions unobtrusive for long-form learning | < 1% of assessment sessions interrupted by session expiry |

### 4.3 Scope

**In scope**

- Self-service registration with email verification
- Email and password sign-in
- Session establishment and renewal via signed tokens
- Sign-out, including sign-out across all devices
- Forgotten-password reset by email
- Password change by an authenticated user
- Rate limiting and account lockout on repeated failures
- Role attribution (learner, instructor, administrator) within the issued session credential

**Out of scope for this release**

- Social sign-in (Google, Microsoft, Apple)
- Enterprise SSO / SAML / SCIM provisioning
- Multi-factor authentication
- Passwordless or magic-link sign-in
- Bulk learner import by administrators
- Fine-grained permission management beyond the three defined roles

Out-of-scope items are candidates for the platform roadmap and should not be designed out of the data model — see §4.8.

### 4.4 Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| Learners | Fast, low-friction access; confidence their data is safe |
| Instructors | Reliable attribution of learners to enrolments and submissions |
| Platform administrators | Manageable support load; ability to suspend accounts |
| Security & compliance | Defensible credential handling and audit trail |
| Product management | Registration conversion and activation metrics |
| Engineering | Clear, testable requirements with unambiguous edge-case handling |

### 4.5 Functional Requirements

| Ref | Requirement | Priority | Stories |
|-----|-------------|----------|---------|
| FR-1 | A visitor can register with email address and password | Must | US-AUTH-01 |
| FR-2 | Registered addresses must be verified before the account becomes active | Must | US-AUTH-02 |
| FR-3 | Email addresses are unique per account, normalised case-insensitively | Must | US-AUTH-03 |
| FR-4 | A verified user can sign in with email and password | Must | US-AUTH-04 |
| FR-5 | Repeated failed attempts trigger throttling and temporary lockout | Must | US-AUTH-05 |
| FR-6 | Successful authentication issues a short-lived access credential and a longer-lived renewal credential | Must | US-AUTH-07 |
| FR-7 | Sessions renew without user interaction while the renewal credential is valid | Must | US-AUTH-08 |
| FR-8 | Users can terminate the current session and all sessions | Must | US-AUTH-09 |
| FR-9 | Session credentials carry role and status for authorisation decisions | Must | US-AUTH-10 |
| FR-10 | Users can request a password reset by email | Must | US-AUTH-11 |
| FR-11 | Reset links are single-use and expire after 30 minutes | Must | US-AUTH-12, 13 |
| FR-12 | Completing a reset terminates all other active sessions | Must | US-AUTH-13 |
| FR-13 | Authenticated users can change their password with current-password confirmation | Should | US-AUTH-14 |
| FR-14 | Users are returned to their originally requested destination after sign-in | Should | US-AUTH-06 |
| FR-15 | Authentication events are recorded for audit and support investigation | Should | All |

### 4.6 Non-Functional Requirements

| Ref | Category | Requirement |
|-----|----------|-------------|
| NFR-1 | Security | Passwords stored using a memory-hard adaptive hash with per-user salt; plaintext never logged, cached or returned |
| NFR-2 | Security | Registration, sign-in and reset responses must not reveal whether an address is registered |
| NFR-3 | Security | All authentication traffic over TLS; renewal credential held in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie, never in browser storage accessible to scripts |
| NFR-4 | Security | Signing keys held in managed secret storage, rotatable without invalidating in-flight access tokens beyond their natural 15-minute lifetime |
| NFR-5 | Performance | Sign-in completes within 500 ms at the 95th percentile under expected peak load, excluding email dispatch |
| NFR-6 | Reliability | Email dispatch is queued and retried; failure to send does not roll back account creation, and the user is offered a resend |
| NFR-7 | Usability | All forms are keyboard-navigable and meet WCAG 2.2 AA, with errors announced to assistive technology |
| NFR-8 | Privacy | Personal data limited to email, display name and authentication metadata; deletion request removes or anonymises within the platform-wide retention policy |
| NFR-9 | Auditability | Registration, sign-in success and failure, lockout, reset request and completion, and sign-out are logged with timestamp, user reference and source IP, retained 12 months |

### 4.7 Business Rules

- **BR-1** — Password policy: minimum 10 characters, no maximum below 128, rejected if present on the common-breached-password list. No mandatory composition rules (aligns with NIST SP 800-63B guidance).
- **BR-2** — Email address is the unique account identifier and cannot be changed in this release.
- **BR-3** — Account statuses are `pending_verification`, `active`, `locked`, `suspended`, `deactivated`. Only `active` accounts may authenticate.
- **BR-4** — Verification links expire after 24 hours; reset links after 30 minutes.
- **BR-5** — Lockout threshold is 5 consecutive failures; lockout duration 15 minutes, self-clearing.
- **BR-6** — Every account holds exactly one role; the default on registration is `learner`.
- **BR-7** — Access credential lifetime 15 minutes; renewal credential lifetime 7 days with rotation on each use.

### 4.8 Assumptions

- A transactional email provider is available and configured for the LearnFlow sending domain, with SPF/DKIM/DMARC in place.
- Learners register as individuals; organisational or cohort-based bulk provisioning is deferred.
- Email verification is an acceptable trade-off against registration conversion for this audience; this should be validated against activation data post-launch.
- The user data model will accommodate future external identity providers (a nullable provider reference) even though none are implemented now.
- Legal and privacy copy — terms of use, privacy notice — is supplied by the business before build completion.

### 4.9 Dependencies

| Dependency | Owner | Impact if unavailable |
|------------|-------|-----------------------|
| Transactional email service | Platform engineering | Registration and reset flows cannot complete |
| Secret management for signing keys | Platform engineering | Token issuing cannot be secured for production |
| Terms of use and privacy notice | Legal / Compliance | Registration screen cannot be released |
| Email template design | Design | Verification, reset and security notifications blocked |
| Rate-limiting infrastructure | Platform engineering | FR-5 and NFR partially unmet; launch risk |

### 4.10 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Verification emails routed to spam, suppressing activation | Medium | High | Domain authentication, deliverability testing pre-launch, resend option, monitor verification rate |
| Credential-stuffing attack using breached password lists | Medium | High | Lockout, IP rate limiting, breached-password screening at registration and reset |
| Reset-link interception via forwarded or logged URLs | Low | High | Short expiry, single use, session revocation on use, no tokens in server access logs |
| Users frustrated by session expiry during long assessments | Medium | Medium | Silent renewal, client-side draft preservation, monitor interrupted-session metric |
| Enumeration of registered addresses through timing or message differences | Medium | Medium | Uniform responses and comparable response timing across all identity-revealing endpoints |

### 4.11 Success Metrics (90 days post-launch)

- Registration completion rate (form started → verified) ≥ 70%
- Sign-in success rate ≥ 98% of attempts by verified users
- Password-reset completion rate (requested → completed) ≥ 80%
- Access-related support tickets < 2% of monthly active users
- Zero confirmed credential-compromise incidents

### 4.12 Open Questions

1. Should email verification be mandatory before first sign-in, or should limited browsing be permitted with a nag prompt? Trade-off between conversion and data quality — recommend a product decision before build.
2. Is a display name captured at registration, or deferred to profile completion?
3. What is the retention period for accounts that never complete verification? Recommend automated purge at 30 days.
4. Does the business require an administrator-initiated password reset path for support cases in this release?
5. Should the 7-day renewal credential lifetime differ for instructor and administrator roles, given their higher privilege?

---

*End of section. Stories are ready for estimation; open questions in §4.12 should be resolved before sprint planning.*
