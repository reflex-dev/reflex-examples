# Local Authentication Example

See example app code: [`local_auth.py`](./local_auth/local_auth.py)

## Models

This example makes use of two models, [`User`](./local_auth/user.py) and
[`AuthSession`](./local_auth/auth_session.py), which store user login
information and authenticated user sessions respectively.

User passwords are hashed in the database with
[`passlib`](https://pypi.org/project/passlib/) using
[`bcrypt`](https://pypi.org/project/bcrypt/) algorithm. However, during
registration and login, the unhashed password is sent over the websocket, so
**it is critical to use TLS to protect the websocket connection**.

## States

The base [`State`](./local_auth/base_state.py) class stores the `auth_token` as
a `LocalStorage` var, allowing logins to persist across browser tabs and
sessions.

It also exposes `authenticated_user` as a cached computed var, which
looks up the `auth_token` in the `AuthSession` table and returns a matching
`User` if any exists. The `is_authenticated` cached var is a convenience for
determining whether the `auth_token` is associated with a valid user.

The public event handler, `do_logout`, may be called from the frontend and will
destroy the `AuthSession` associated with the current `auth_token`.

The private event handler, `_login` is only callable from the backend, and
establishes an `AuthSession` for the given `user_id`. It assumes that the
validity of the user credential has already been established, which is why it is
a private handler.

### Registration

The [`RegistrationState`](./local_auth/registration.py) class handles the
submission of the register form, checking for input validity and ultimately
creating a new user in the database.

After successful registration, the event handler redirects back to the login
page after a brief delay.

### Login

The [`LoginState`](./local_auth/login.py) class handles the submission of the
login form, checking the user password, and ultimately redirecting back to the
last page that requested login (or the index page).

The `LoginState.redir` event handler is a bit special because it behaves
differently depending on the page it is called from.

  * If `redir` is called from any page except `/login` and there is no
    authenticated user, it saves the current page route as `redirect_to` and
    forces a redirect to `/login`.
  * If `redir` is called from `/login` and the there is an authenticated
    user, it will redirect to the route saved as `redirect_to` (or `/`)

## Forms and Flow

### `@require_login`

The `login.require_login` decorator is intended to be used on pages that require
authentication to be viewed. It uses `rx.cond` to conditionally render either
the wrapped page, or some loading spinners as placeholders. Because one of the
spinners specifies `LoginState.redir` as the event handler for its `on_mount`
trigger, it will handle redirection to the login page if needed.

### Login Form

The login form triggers `LoginState.on_submit` when submitted, and this function
is responsible for looking up the user and validating the password against the
database. Once the user is authenticated, `State._login` is called to create the
`AuthSession` associating the `user_id` with the `auth_token` stored in the
browser's `LocalStorage` area.

Finally `on_submit` chains back into `LoginState.redir` to handle redirection
back to the page that requested the login (stored as `LoginState.redirect_to`).

### Protect the State

Keep in mind that **all pages in a reflex app are publicly accessible**! The
`redir` mechanism is designed to get users to and from the login page, it is NOT
designed to protect private data.

All private data needs to originate from computed vars or event handlers setting
vars after explicitly checking `State.authenticated_user` on the backend.
Static data passed to components, even on protected pages, can be retrieved
without logging in. It cannot be stressed enough that **private data MUST come
from the state**.
