# LearnFlow — Authentication (Registration, Login, JWT, Password Reset)

## 1. User Stories

**US-01 — Registration**
As a **prospective learner**, I want to **create a LearnFlow account with my email and a password**, so that **I can access the platform under my own identity**.

**US-02 — Login**
As a **registered learner**, I want to **sign in with my email and password**, so that **I can reach my dashboard and courses**.

**US-03 — JWT issuing**
As a **signed-in learner**, I want **the platform to issue me a session token on successful login**, so that **I can navigate and call the API without re-entering my password on every request**.

**US-04 — Password reset**
As a **learner who forgot my password**, I want to **request a reset link by email and set a new password**, so that **I can regain access without contacting support**.

## 2. Acceptance Criteria

### US-01 — Registration
- **Given** an unauthenticated visitor **When** they submit a valid email, a password meeting policy, and a matching confirmation **Then** an account is created with a hashed password (never plaintext) and a success response is returned.
- **Given** a submitted password fails policy (e.g. under 10 characters) **When** the form is submitted **Then** the account is not created and the specific rule violated is shown inline.
- **Given** an account already exists for the submitted email **When** registration is attempted **Then** the same generic success response is returned (no account-existence disclosure), and no duplicate row is created.

### US-02 — Login
- **Given** a registered account **When** correct email and password are submitted **Then** the user is authenticated and redirected to their dashboard.
- **Given** an incorrect password or unregistered email **When** login is attempted **Then** an identical generic failure message is returned in both cases, with comparable response timing.
- **Given** repeated failed attempts on one account **When** a threshold is exceeded **Then** the account is temporarily locked and further attempts are refused regardless of credential correctness.

### US-03 — JWT issuing
- **Given** authentication succeeds **When** tokens are issued **Then** a short-lived access token is returned to the client and a longer-lived refresh token is set as an `HttpOnly`, `Secure` cookie.
- **Given** an access token payload is inspected **When** decoded **Then** it contains subject, role, issued-at and expiry claims, and no password or sensitive data.
- **Given** a request carries an expired, malformed, or invalidly signed token **When** it reaches a protected endpoint **Then** the API returns HTTP 401 and no business logic executes.

### US-04 — Password reset
- **Given** a learner on the forgotten-password page **When** any syntactically valid email is submitted **Then** the same neutral confirmation is shown regardless of whether the account exists.
- **Given** an account exists for the submitted address **When** the request is processed **Then** a single-use, time-limited reset token is generated and emailed; only its hash is persisted.
- **Given** a valid, unexpired reset token **When** a new password meeting policy is submitted **Then** the password hash is replaced, the token is consumed, and the user is redirected to sign in.
- **Given** an expired or already-used reset token **When** submitted **Then** the reset is refused with a message offering to restart the flow, without revealing which condition failed.

## 3. BRD Section — Authentication & Account Access

**Purpose:** Authentication is the entry point to every LearnFlow capability — enrolment, progress tracking, and certification all depend on a reliable, attributable user identity.

**Scope (in):** self-service registration, email/password login, JWT-based session issuing, password reset by email.
**Scope (out):** social login/SSO, MFA, passwordless login — candidates for a later release.

**Functional Requirements**

| Ref | Requirement | Priority |
|-----|-------------|----------|
| FR-1 | Visitor can register with email + password | Must |
| FR-2 | Registered user can sign in with email + password | Must |
| FR-3 | Successful login issues a short-lived access token + longer-lived refresh token | Must |
| FR-4 | User can request and complete a password reset via emailed link | Must |
| FR-5 | Repeated failed logins trigger throttling/lockout | Must |

**Non-Functional Requirements**
- Passwords stored with a memory-hard, per-user-salted hash; plaintext never logged.
- Auth traffic over TLS only; refresh token never exposed to client-side scripts.
- Login/registration/reset responses must not reveal whether an email is registered.

**Business Rules**
- Password minimum 10 characters; reject known-breached passwords.
- Reset links single-use, short-lived (recommend 30 minutes).
- Access token lifetime short (recommend 15 minutes); refresh token longer (recommend 7 days), rotated on use.
