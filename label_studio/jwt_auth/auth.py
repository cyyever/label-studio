import logging

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class TokenAuthenticationPhaseout(TokenAuthentication):
    """TokenAuthentication with features to help phase out legacy token auth

    Logs usage and triggers a 401 if legacy token auth is not enabled for the organization."""

    def authenticate(self, request):
        """Authenticate the request and log if successful."""
        from core.current_request import CurrentContext
        from core.feature_flags import flag_set

        auth_result = super().authenticate(request)

        # Update CurrentContext with authenticated user
        if auth_result is not None:
            user, _ = auth_result
            CurrentContext.set_user(user)

        return auth_result


class JWTAuthScheme(OpenApiAuthenticationExtension):
    target_class = 'jwt_auth.auth.TokenAuthenticationPhaseout'
    name = 'Token'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'The token (or API key) must be passed as a request header. '
            'You can find your user token on the User Account page in Label Studio. Example: '
            '<br><pre><code class="language-bash">'
            'curl https://label-studio-host/api/projects -H "Authorization: Token [your-token]"'
            '</code></pre>',
            'x-fern-header': {
                'name': 'api_key',
                'env': 'LABEL_STUDIO_API_KEY',
                'prefix': 'Token ',
            },
        }
