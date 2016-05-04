from apps import api
from users.views import *
from payments.views import *
from jobs.generic.views import JobSettingsView
from jobs.ping.views import *


def add_resource():
	api.add_resource(UserSignUptView, '/user/signup/')
	api.add_resource(UserDetailsView, '/user/details/')
	api.add_resource(UpdateProfileView, '/user/update-profile/')
	api.add_resource(UpdateLogoView, '/user/update-logo/')
	api.add_resource(ChangePasswordView, '/user/change-password/')
	api.add_resource(SubAccountView, '/user/sub-account/')
	api.add_resource(UpdateSubAccountView, '/user/sub-account/<user_id>/')
	api.add_resource(CardDetailsView, '/user/card-details/')
	api.add_resource(MessageView, '/user/messages/')
	api.add_resource(MessageDetailView, '/user/messages/<message_id>/')
	api.add_resource(SubAccountChangePermissionView, '/user/sub-account-permission/<user_id>/')
	api.add_resource(ContactGroupView, '/user/contact-group/')
	api.add_resource(ContactGroupDetailView, '/user/contact-group/<group_id>/')
	api.add_resource(ContactGroupingView, '/user/contact-grouping/')
	api.add_resource(PlanDetailsView, '/user/plan-details/')
	api.add_resource(ForgotPasswordView, '/user/password-reset/')
	api.add_resource(ResetPasswordView, '/user/password-reset-confirm/')
