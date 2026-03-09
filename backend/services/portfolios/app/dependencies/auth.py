from shared.dependencies import auth

deps = auth.create_dependencies()

CurrentUser = deps.CurrentUser
CurrentUserOrNone = deps.CurrentUserOrNone
