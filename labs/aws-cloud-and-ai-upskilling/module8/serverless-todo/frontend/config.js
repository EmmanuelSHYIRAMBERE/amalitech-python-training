// Filled in with real deployed values after `sam deploy` — see the
// stack's Outputs (UserPoolId, UserPoolClientId, ApiUrl). Amplify
// Hosting injects these as build-time environment variables per the
// lab's rubric ("properly configured... via environment variables");
// amplify.yml's build step writes this file from those env vars before
// publishing, so this placeholder is never what actually ships.
window.APP_CONFIG = {
  region: "eu-north-1",
  userPoolId: "REPLACE_WITH_USER_POOL_ID",
  userPoolClientId: "REPLACE_WITH_USER_POOL_CLIENT_ID",
  apiUrl: "REPLACE_WITH_API_URL",
};
