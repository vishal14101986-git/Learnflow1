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

## Appendix A — Authentication Edge Case Register

Every case below is a testable scenario with defined expected behaviour. Cases marked **⚠** are ones where the naive implementation is wrong in a way that is easy to ship and hard to notice.

### A.1 Registration — Duplicate Email

**EC-R-01 — Duplicate of an active, verified account**
- **Given** an active verified account exists for `learner@example.com`
  **When** a visitor submits a registration for `learner@example.com`
  **Then** the API returns the same neutral success response used for a genuine registration, no second account row is created, and the address owner receives a "someone tried to register with your address" email containing sign-in and password-reset links but no new verification link.

**EC-R-02 — Duplicate of an account still pending verification ⚠**
- **Given** an account for `learner@example.com` exists in `pending_verification` status and was created 3 days ago
  **When** a visitor submits a registration for that address with a *different* password
  **Then** the existing password hash is **not** overwritten, no new account is created, the neutral success response is returned, and a fresh verification email is sent to the address — so a genuine owner who never received the first email can proceed, while a third party cannot seize a pending registration.

**EC-R-03 — Duplicate differing only by case or surrounding whitespace**
- **Given** an account exists for `learner@example.com`
  **When** a visitor registers as ` Learner@Example.COM `
  **Then** the input is trimmed and the address normalised to lower case before the uniqueness check, and the request is treated exactly as EC-R-01.

**EC-R-04 — Duplicate differing by provider-specific aliasing ⚠**
- **Given** an account exists for `learner@gmail.com`
  **When** a visitor registers as `lear.ner+lms@gmail.com`
  **Then** the registration is accepted as a distinct account, because LearnFlow does not apply provider-specific alias collapsing. *(This is a deliberate decision — see §4.12; if the business wants one-person-one-account enforcement, it needs a different identity strategy than email normalisation.)*

**EC-R-05 — Concurrent duplicate submissions**
- **Given** no account exists for `learner@example.com`
  **When** two registration requests for that address are processed concurrently by different application workers
  **Then** the unique index on the normalised email column causes one insert to fail, the failing request is handled as EC-R-01 rather than returning a database error, and exactly one account row exists.

**EC-R-06 — Registration attempt while already signed in**
- **Given** I hold a valid session
  **When** I submit the registration form
  **Then** the request is refused and I am redirected to my dashboard with a message that I am already signed in.

**EC-R-07 — Duplicate of a deactivated account**
- **Given** an account for `learner@example.com` exists in `deactivated` status
  **When** a visitor registers with that address
  **Then** no new account is created, the neutral success response is returned, and the address receives an email directing them to support for reactivation — the historical learning record is not orphaned by a second account.

### A.2 Registration — Weak Password

**EC-P-01 — Below minimum length**
- **Given** I am on the registration form
  **When** I submit a password of fewer than 10 characters
  **Then** the account is not created and the message states the minimum length explicitly rather than a generic "invalid password".

**EC-P-02 — Present on the breached-password list**
- **Given** I submit a password appearing on the configured breached/common-password list
  **When** the password is validated server-side
  **Then** the registration is refused with a message explaining the password has appeared in known breaches and must be changed, and the rejected value is not written to any log.

**EC-P-03 — Password derived from the account identifier**
- **Given** I register as `jane.doe@example.com`
  **When** I submit a password containing the local part of my email or my display name (case-insensitive)
  **Then** the registration is refused with an explanation.

**EC-P-04 — Whitespace padding used to reach minimum length ⚠**
- **Given** I submit `pass      ` (four characters plus trailing spaces)
  **When** the password is validated
  **Then** leading and trailing whitespace is stripped **before** the length check, the effective length of 4 fails policy, and the account is not created. Internal whitespace is preserved and permitted.

**EC-P-05 — Excessively long password ⚠**
- **Given** I submit a password of 5,000 characters
  **When** the request is processed
  **Then** it is rejected above 128 characters at the validation layer before any hashing occurs, so a long input cannot be used as a CPU-exhaustion denial-of-service vector.

**EC-P-06 — Multi-byte and emoji characters**
- **Given** I submit a password containing emoji or non-Latin script
  **When** it is validated and stored
  **Then** it is normalised consistently (NFKC) before hashing, accepted if it meets length policy measured in characters rather than bytes, and authenticates successfully on subsequent sign-in.

**EC-P-07 — Confirmation mismatch**
- **Given** I complete the registration form
  **When** the password and confirmation fields differ
  **Then** submission is blocked, both fields retain focus affordance, and no request reaches the server.

**EC-P-08 — Client-side validation bypassed**
- **Given** a caller posts directly to the registration endpoint with a 3-character password, bypassing the React form
  **When** the request is processed
  **Then** the same server-side policy applies and the account is not created — client-side validation is treated as a convenience only.

**EC-P-09 — Weak password submitted at reset rather than registration**
- **Given** I hold a valid reset token
  **When** I submit a new password failing any policy rule
  **Then** the identical policy and messages apply, the token is **not** consumed, and I may retry with the same link.

### A.3 Tokens — Expiry and Validity

**EC-T-01 — Expired access token on a routine request**
- **Given** my access token expired 30 seconds ago and my refresh token is valid
  **When** the client calls a protected endpoint
  **Then** the API returns HTTP 401 with a machine-readable `token_expired` code, the client transparently refreshes and replays the original request once, and I observe no interruption.

**EC-T-02 — Expired access token during an in-flight long request ⚠**
- **Given** I begin an assignment upload with 90 seconds of token validity remaining and the upload takes 4 minutes
  **When** the request completes
  **Then** authorisation is evaluated at request admission, not at completion, so the upload succeeds; the subsequent request triggers a normal refresh.

**EC-T-03 — Expired refresh token**
- **Given** my refresh token expired while I was away
  **When** the client attempts renewal
  **Then** renewal is refused, the cookie is cleared, I am returned to sign-in with the return path preserved, and any unsaved client-side draft is retained locally so it survives re-authentication.

**EC-T-04 — Reuse of an already-rotated refresh token ⚠**
- **Given** refresh token `A` was exchanged for token `B`
  **When** token `A` is presented again
  **Then** the request is refused, the entire token family for that user is revoked, all sessions terminate, and a security event is raised — reuse is treated as evidence of theft, not as a retry.

**EC-T-05 — Concurrent refresh from two browser tabs ⚠**
- **Given** two tabs detect expiry simultaneously and both call refresh with the same token
  **When** the requests are processed
  **Then** a short reuse-grace window (or single-flight locking in the client) allows the second call to receive the same newly issued pair rather than triggering the EC-T-04 theft response — a legitimate race must not sign the user out.

**EC-T-06 — Tampered payload or `alg: none`**
- **Given** a token whose payload has been edited to elevate the role, or whose header declares `none`
  **When** it is presented to a protected endpoint
  **Then** signature verification fails against the explicitly configured algorithm, the request returns 401, and the attempt is logged with source IP.

**EC-T-07 — Valid signature, wrong issuer or audience**
- **Given** a correctly signed token issued by a non-production LearnFlow environment
  **When** it is presented to production
  **Then** issuer and audience claims are validated and the request is refused.

**EC-T-08 — Token valid but the underlying account has changed state ⚠**
- **Given** an administrator suspends my account while I hold an access token with 12 minutes remaining
  **When** I call a protected endpoint
  **Then** account status is checked on each request against a cached status lookup, not inferred solely from the token, and the request is refused with 403.

**EC-T-09 — Role elevated mid-session**
- **Given** my role is upgraded from `learner` to `instructor`
  **When** I call an instructor endpoint before my next refresh
  **Then** the request is refused with 403 until the refreshed token carries the new role; the UI surfaces a "sign in again to activate new permissions" prompt rather than an unexplained error.

**EC-T-10 — Signing key rotated**
- **Given** the signing key is rotated
  **When** a token signed with the previous key is presented within its remaining lifetime
  **Then** verification succeeds against the retired key while it remains in the published key set, and fails once the key is withdrawn after the maximum token lifetime has elapsed.

**EC-T-11 — Clock skew between client and server**
- **Given** a client clock is 40 seconds ahead of the server
  **When** a freshly issued token is presented
  **Then** a small leeway (≤ 60 seconds) is applied to `nbf`/`iat` validation so the token is not rejected as not-yet-valid.

**EC-T-12 — Access token replayed after sign-out**
- **Given** I signed out 2 minutes ago and my access token has 8 minutes of nominal life left
  **When** that token is replayed
  **Then** the request is refused because its token ID is on the revocation list, which is retained for at least the access-token lifetime.

### A.4 Password Reset — Non-Existent and Ineligible Accounts

**EC-X-01 — Reset requested for an address with no account ⚠**
- **Given** no account exists for `nobody@example.com`
  **When** a reset is requested for it
  **Then** the response is byte-identical to the success case, no email is sent to that address, no token row is created, and the response is padded to comparable timing so the absence of hashing and email queuing work is not observable.

**EC-X-02 — Reset requested for a syntactically invalid address**
- **Given** the submitted value is not a valid email address
  **When** the form is submitted
  **Then** it is rejected as a format error — this is the one case where a distinct message is acceptable, since it reveals nothing about account existence.

**EC-X-03 — Reset requested for an unverified account**
- **Given** an account exists in `pending_verification` status
  **When** a reset is requested
  **Then** the neutral response is returned and the email sent contains a verification link rather than a reset link, so the flow cannot be used to activate an address the requester does not control.

**EC-X-04 — Reset requested for a suspended account**
- **Given** an account is `suspended`
  **When** a reset is requested
  **Then** the neutral response is returned, no reset token is issued, and the account owner receives a message directing them to support.

**EC-X-05 — Reset requested for a locked account**
- **Given** an account is locked following failed sign-in attempts
  **When** a reset is requested and successfully completed
  **Then** the lock is cleared and the failed-attempt counter resets, so a legitimate owner is not compelled to wait out the lockout.

**EC-X-06 — Enumeration attempt across many addresses**
- **Given** a caller submits reset requests for 500 addresses in sequence
  **When** the requests are processed
  **Then** per-IP rate limiting rejects the excess with HTTP 429, and the responses returned before the limit is reached are indistinguishable between existing and non-existing accounts.

### A.5 Password Reset — Token Handling

**EC-X-07 — Expired reset token**
- **Given** my reset token was issued 45 minutes ago
  **When** I submit a new password
  **Then** the reset is refused with a message offering to request a fresh link, no password change occurs, and the message does not distinguish expiry from any other invalid-token condition.

**EC-X-08 — Reset token used a second time**
- **Given** I completed a reset using token `T`
  **When** I open the same link again and submit
  **Then** the reset is refused identically to EC-X-07.

**EC-X-09 — Superseded token**
- **Given** I requested a reset twice and hold tokens `T1` (older) and `T2`
  **When** I use `T1`
  **Then** it is refused, because issuing `T2` invalidated `T1`; using `T2` succeeds.

**EC-X-10 — Email security scanner pre-fetches the link ⚠**
- **Given** my organisation's mail gateway automatically visits every URL in inbound email
  **When** the reset link is fetched by the scanner
  **Then** the GET request only renders the form and does **not** consume or invalidate the token; consumption happens exclusively on the POST that submits the new password, so the link still works when I click it.

**EC-X-11 — Reset token value exposure**
- **Given** a reset link is requested
  **When** application and proxy logs are inspected
  **Then** the token appears in no access log, error report or analytics payload; where the token is carried in the URL path or query, log scrubbing is applied at the edge.

**EC-X-12 — New password identical to the current one**
- **Given** I hold a valid reset token
  **When** I submit my existing password as the new one
  **Then** the change is refused with a clear message and the token remains usable for a further attempt.

**EC-X-13 — Concurrent reset submissions with one token**
- **Given** I submit the reset form twice in rapid succession with the same token
  **When** both requests are processed
  **Then** the token consumption is atomic — one request succeeds and the other is refused as already-used, with no possibility of two different passwords being written.

**EC-X-14 — Sessions elsewhere after a completed reset**
- **Given** I am signed in on a second device
  **When** I complete a password reset on my laptop
  **Then** the second device's next request or refresh fails and returns to sign-in, since all refresh tokens for the account were revoked.

**EC-X-15 — Reset completed in a different browser or device from the request**
- **Given** I requested the reset on desktop and open the link on my phone
  **When** I submit the new password
  **Then** the reset succeeds — reset validity depends only on the token, never on session, cookie or device continuity.

### A.6 Cross-Cutting

**EC-C-01 — Correct password on an unverified account**
- **Given** my account is `pending_verification`
  **When** I sign in with correct credentials
  **Then** no token is issued and I am shown the verification-outstanding message with a resend option — verification state is checked before token issuance, not after.

**EC-C-02 — Sign-in attempt against a non-existent account ⚠**
- **Given** no account exists for the submitted address
  **When** sign-in is attempted
  **Then** a dummy hash comparison of equivalent cost is still performed before returning the generic failure, so response timing does not disclose account existence.

**EC-C-03 — Account locked, correct password supplied**
- **Given** my account is locked
  **When** I sign in with the correct password
  **Then** sign-in is refused for the remainder of the lockout window, and the failed-attempt counter is not incremented further by attempts made during the lock.

**EC-C-04 — Password changed in another session**
- **Given** I changed my password on another device
  **When** my current session's refresh token is presented
  **Then** it is refused and I am returned to sign-in.

**EC-C-05 — Email dispatch fails after the account row is committed ⚠**
- **Given** account creation succeeds but the verification email cannot be queued
  **When** the transaction completes
  **Then** the account is retained in `pending_verification`, the user still sees the confirmation screen with a working resend control, and the failure is alerted to operations — a mail outage must not produce accounts that can never be verified or silently lose registrations.

**EC-C-06 — Unverified accounts never completed**
- **Given** an account has remained `pending_verification` for 30 days
  **When** the scheduled retention job runs
  **Then** the account and its tokens are purged, freeing the address for future registration.

---

*End of section. Stories and edge cases are ready for estimation; open questions in §4.12 should be resolved before sprint planning.*
