from shared.dependencies import auth

deps = auth.create_dependencies()

CurrentUser = deps.CurrentUser

require_admin = deps.require_admin
require_user = deps.require_user
