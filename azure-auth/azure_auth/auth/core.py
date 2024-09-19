from urllib.parse import parse_qs, urlparse
import msal
import reflex as rx
from typing import Dict

client_id: str = "0df2a88e-fddb-4cc2-b3e0-f475f162b373"
client_secret: str = ""
tenant_id: str = "f2c9cbbe-006b-46b8-9ad0-d877d8446d6d"
redirect_uri: str = "http://localhost:3000/callback"
authority = f"https://login.microsoftonline.com/{tenant_id}"
login_redirect = "/home"
cache = msal.TokenCache()


sso_app: msal.ClientApplication = (
    msal.ConfidentialClientApplication
    if client_secret
    else msal.PublicClientApplication
)(
    client_id=client_id,
    client_credential=client_secret,
    authority=authority,
    token_cache=cache,
)


class State(rx.State):
    token: Dict[str, str] = {}
    access_token: str = " "
    flow: dict

    def redirect_sso(self, scope=[]) -> rx.Component:
        self.flow = sso_app.initiate_auth_code_flow(
            scopes=scope, redirect_uri=redirect_uri
        )
        return rx.redirect(self.flow["auth_uri"])

    def require_auth(self):
        if not self.token:
            rx.input()
            return self.redirect_sso()

    @rx.var
    def check_auth(self):
        return True if self.token else False

    def logout(self):
        self.token = {}
        return rx.redirect(authority + "/oauth2/v2.0/logout")

    def callback(self):
        query_components = parse_qs(urlparse(self.router.page.raw_path).query)

        auth_response = {
            "code": query_components["code"][0],
            "client_info": query_components["client_info"][0],
            "state": query_components["state"][0],
            "session_state": query_components["session_state"][0],
            "client-secret": client_secret,
        }
        result = sso_app.acquire_token_by_auth_code_flow(
            self.flow, auth_response, scopes=[]
        )
        self.access_token = result[
            "access_token"
        ]  # this can be used for accessing graph
        self.token = result["id_token_claims"]
        return rx.redirect(login_redirect)
