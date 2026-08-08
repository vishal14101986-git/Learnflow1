# LearnFlow LMS — Authentication & Account Access

## 1. User Stories

### Registration
- **As a** prospective learner, **I want** to create an account with my email and a password **so that** I can access LearnFlow's courses.
- **As a** new user, **I want** to receive confirmation that my account was created successfully **so that** I know I can proceed to log in.
- **As a** platform owner, **I want** duplicate email registrations to be rejected **so that** each account maps to a unique identity.

### Login
- **As a** registered user, **I want** to log in with my email and password **so that** I can access my courses and dashboard.
- **As a** registered user, **I want** to receive a clear error when my credentials are wrong **so that** I understand why I couldn't log in without exposing which field was incorrect.
- **As a** returning user, **I want** my session to stay active for a reasonable period **so that** I'm not forced to log in repeatedly during normal use.

### JWT Issuing
- **As a** logged-in user, **I want** the system to issue a signed access token on successful login **so that** subsequent API requests can authenticate me without resending credentials.
- **As a** frontend client, **I want** an access token with a short expiry plus a refresh token **so that** the session can be renewed securely without re-prompting for a password.
- **As a** platform owner, **I want** JWTs to carry minimal claims (user ID, role, expiry) **so that** the token cannot leak sensitive data if intercepted.

### Password Reset
- **As a** user who forgot their password, **I want** to request a password reset via email **so that** I can regain access to my account without contacting support.
- **As a** user resetting my password, **I want** the reset link to expire after a short window **so that** old links can't be used to compromise my account.
- **As a** user, **I want** all active sessions/tokens invalidated after a password reset **so that** anyone who had access to my old credentials is logged out.

---

## 2. Acceptance Criteria

### Registration
**Scenario: Successful registration**
- Given a visitor on the registration page with a valid, unregistered email and a password meeting complexity rules
- When they submit the registration form
- Then the system creates a new user record with a hashed password, returns HTTP 201, and sends a confirmation response (or verification email, if applicable)

**Scenario: Duplicate email**
- Given an email address that already exists in the system
- When a visitor attempts to register with that email
- Then the system returns HTTP 409 with a generic "email already in use" message and does not create a duplicate record

**Scenario: Weak password**
- Given a password that does not meet minimum complexity requirements (e.g., <8 characters)
- When the visitor submits the registration form
- Then the system returns HTTP 422 with field-level validation errors and does not create the account

### Login
**Scenario: Successful login**
- Given a registered user with valid credentials
- When they submit their email and password to the login endpoint
- Then the system verifies the password hash, returns HTTP 200, and issues a JWT access token (and refresh token)

**Scenario: Invalid credentials**
- Given an email/password combination that does not match a valid account
- When the user attempts to log in
- Then the system returns HTTP 401 with a generic "invalid email or password" message (without indicating whether the email or password was wrong)

**Scenario: Account locked/rate-limited**
- Given repeated failed login attempts (e.g., 5+ within 15 minutes) for the same account
- When the user attempts another login
- Then the system returns HTTP 429 and temporarily blocks further attempts for that account/IP

### JWT Issuing
**Scenario: Access token issued on login**
- Given valid login credentials
- When authentication succeeds
- Then the system issues a JWT signed with the server's secret/key, containing `sub` (user ID), `role`, `iat`, and `exp` claims, with an expiry of ~15 minutes

**Scenario: Refresh token flow**
- Given a valid, unexpired refresh token
- When the client calls the refresh endpoint
- Then the system issues a new access token without requiring re-authentication

**Scenario: Expired or tampered token**
- Given an expired or invalid-signature JWT sent with an API request
- When the request hits a protected endpoint
- Then the system returns HTTP 401 and does not process the request

### Password Reset
**Scenario: Reset request**
- Given a user who submits their email on the "forgot password" form
- When the email matches a registered account
- Then the system generates a time-limited reset token, emails a reset link, and returns HTTP 200 (identical response is returned even if the email does not exist, to prevent user enumeration)

**Scenario: Successful password reset**
- Given a valid, unexpired reset token and a new password meeting complexity rules
- When the user submits the new password via the reset link
- Then the system updates the password hash, invalidates the reset token, revokes existing refresh tokens/sessions, and returns HTTP 200

**Scenario: Expired or reused reset token**
- Given a reset token that is expired or already used
- When the user attempts to reset their password with it
- Then the system returns HTTP 400 and does not update the password

---

## 3. BRD Section — Authentication & Account Access

**Purpose**
Enable users to self-register, authenticate, and recover account access on LearnFlow, establishing the identity foundation for all downstream features (course enrollment, progress tracking, role-based access).

**Scope**
- User registration (email + password)
- Login with credential verification
- JWT-based session management (access + refresh tokens)
- Self-service password reset via email

**Out of Scope (this iteration)**
- Social/SSO login (Google, Microsoft, etc.)
- Multi-factor authentication
- Email verification workflow (may be a follow-on story)

**Functional Requirements**
| ID | Requirement |
|----|-------------|
| FR-1 | System shall allow registration with unique email + password, storing passwords as salted hashes (e.g., bcrypt/argon2). |
| FR-2 | System shall authenticate users via email/password and issue a JWT access token plus a refresh token on success. |
| FR-3 | Access tokens shall expire in ≤15 minutes; refresh tokens shall expire in ≤7 days and be revocable. |
| FR-4 | System shall provide a password reset flow via emailed, time-limited, single-use tokens. |
| FR-5 | System shall rate-limit login and reset-request attempts to mitigate brute-force and enumeration attacks. |

**Non-Functional Requirements**
- JWTs signed with a secret/key stored outside source control (e.g., env var, secrets manager).
- All auth endpoints served over HTTPS.
- Passwords never logged or returned in API responses.
- Postgres 17 stores users table with unique constraint on email and indexed lookup.

**Assumptions**
- Frontend (React 19) handles token storage (e.g., httpOnly cookie or memory) and attaches JWT to authenticated requests.
- Email delivery (for password reset) is handled by an existing/planned transactional email service.

**Dependencies**
- FastAPI backend with JWT library (e.g., `python-jose` or `PyJWT`).
- Postgres 17 users table (email, password_hash, created_at, role).
- Email service integration for reset links.

**Success Metrics**
- ≥99% successful login rate for valid credentials.
- Password reset completion rate and time-to-reset tracked post-launch.
- Zero incidents of user enumeration or credential leakage in security review.
