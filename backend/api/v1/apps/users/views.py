import os
import json

from flask import jsonify
from flask_jwt import JWT
from flask_restful import Resource, request, abort
from flask_jwt import jwt_required, current_identity
from werkzeug.security import safe_str_cmp, check_password_hash
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename

from apps import app, db
from decorators import plan_not_expired
from forms import RegisterForm, ProfileUpdateForm, CreateSubAccountForm,\
    UpdateSubAccountForm, LogoUpdateForm, PasswordChangeForm, MessageForm,\
    UpdateSubAccountPermissionForm, CreateContactGroupForm, ContactGroupingForm, \
    ContactGroupRenameForm, PasswordResetForm, ForgotPasswordForm
from models import User, ContactGroup, Message, PasswordReset
from apps.payments.forms import CreditCardForm
from apps.payments.models import CreditCard, Plan
from serializer import ContactGroupSerializer, UserSerializer,\
    CardDetailsSerializer, MessageSerializer, PlanSerializer, BaseUserSerializer


def authenticate(username, password):
    user = User.query.filter(User.username==username).first()
    if user and check_password_hash(user.password, password):
        return user


def identity(payload):
    user_id = payload['identity']
    return User.query.filter(User.id == user_id).first()

jwt = JWT(app, authenticate, identity)


class UserSignUptView(Resource):

    def post(self):
        data = ImmutableMultiDict(request.json)
        register_form = RegisterForm(data, csrf_enabled=False)
        if register_form.validate():
            user = register_form.save()
            return jsonify({"status": "success","data": BaseUserSerializer().dump(user).data})
        return register_form.errors


class UserDetailsView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self):
        user = User.query.filter(User.username==current_identity.username).first()
        return jsonify({"data": UserSerializer().dump(user).data})


class ChangePasswordView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def put(self):
        data = ImmutableMultiDict(request.json)
        change_password_form = PasswordChangeForm(data, csrf_enabled=False)
        if change_password_form.validate():
            obj = User.query.filter(User.username == current_identity.username).first()
            change_password_form.save(obj)
            return jsonify({"status": "success", "message": "Password Changed"})
        return change_password_form.errors


class ForgotPasswordView(Resource):

    def get(self):
        get = request.args
        token = get['token']
        email = get['email']
        user = User.query.filter(User.email==email).first()
        instance = PasswordReset.query.filter(PasswordReset.user==user.id,
                                 PasswordReset.token==token, PasswordReset.expire==False).first()
        if not instance:
            return jsonify({"status": "error", "message": "Invalid Token"})
        return jsonify({"status": "success", "message": "Token Verified"})

    def post(self):
        data = ImmutableMultiDict(request.json)
        forgot_password_form = ForgotPasswordForm(data, csrf_enabled=False)
        if forgot_password_form.validate():
            instance = User.query.filter(User.email == data['email']).first()
            forgot_password_form.send_mail(instance)
            return {"status": "success"}
        return forgot_password_form.errors


class ResetPasswordView(Resource):

    def put(self):
        data = ImmutableMultiDict(request.json)
        reset_password_form = PasswordResetForm(data, csrf_enabled=False)
        if reset_password_form.validate():
            reset_password_form.save()
            return {"status": "success", "message": "Password reset done"}
        return reset_password_form.errors


class UpdateLogoView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def put(self):
        obj = User.query.filter(User.username==current_identity.username).first()
        logo_form = LogoUpdateForm(request.files, csrf_enabled=False)
        if logo_form.validate():
            file = logo_form.logo.data
            file_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            url = app.config['STATIC_FOLDER']+file_name
            logo_form.save(obj, url)
            return jsonify({"status": "success","data": UserSerializer().dump(obj).data})
        return logo_form.errors

    def delete(self):
        db.session.query(User).filter_by(id=current_identity.id).\
            update({"logo_image_name": "", "logo_image_path": ""})
        db.session.commit()
        return '', 204


class UpdateProfileView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def put(self):
        data = ImmutableMultiDict(request.json)
        obj = User.query.filter(User.username==current_identity.username).first()
        update_form = ProfileUpdateForm(data, csrf_enabled=False)
        if update_form.validate():
            profile = update_form.save(obj)
            return jsonify({"status": "success","data": BaseUserSerializer().dump(profile).data})
        return update_form.errors


def abort_if_user_doesnt_exist(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, message="User {} doesn't exist".format(user_id))


def sub_account_validate(sub_account_id):
    obj = User.query.get(sub_account_id)
    if not obj.parent == current_identity.id:
        abort(401, message="Permission denied, User {} is not your child".format(sub_account_id))


def abort_if_not_an_admin():
    if not current_identity.is_admin:
        abort(401, message="Permission denied")


def abort_if_not_a_right_user(user_id):
    if not user_id == current_identity.id:
        abort(401, message="Permission denied")


def abort_if_not_a_right_owner(group_id):
    group = ContactGroup.query.filter(ContactGroup.id == group_id).first()
    if not group.owner == current_identity.id:
        abort(401, message="Permission denied")


class SubAccountView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self):
        users = User.query.filter(User.parent==current_identity.id).all()
        return {"data": BaseUserSerializer().dump(users, many=True).data}

    def post(self):
        data = ImmutableMultiDict(request.json)
        create_form = CreateSubAccountForm(data, csrf_enabled=False)
        if create_form.validate():
            sub_account = create_form.save()
            return jsonify({"status": "success","data": BaseUserSerializer().dump(sub_account).data})
        return create_form.errors


class UpdateSubAccountView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        sub_account_validate(user_id)
        user =  User.query.get(user_id)
        return jsonify({"data": UserSerializer().dump(user).data})

    def put(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        sub_account_validate(user_id)
        obj = User.query.get(user_id)
        data = ImmutableMultiDict(request.json)
        update_form = UpdateSubAccountForm(data, instance=obj, csrf_enabled=False)
        if update_form.validate():
            sub_account = update_form.save(user_id)
            return jsonify({"status": "success", "data": BaseUserSerializer().dump(sub_account).data})
        return update_form.errors

    def delete(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        sub_account_validate(user_id)
        db.session.query(User).filter(User.id==user_id).update({"is_active": False})
        db.session.commit()
        return '', 204


class SubAccountChangePermissionView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def put(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        sub_account_validate(user_id)
        data = ImmutableMultiDict(request.json)
        update_form = UpdateSubAccountPermissionForm(data, csrf_enabled=False)
        if update_form.validate():
            sub_account = update_form.save(user_id)
            return jsonify({"status": "success","data": BaseUserSerializer().dump(sub_account).data})
        return update_form.errors


class CardDetailsView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self):
        card_details = CreditCard.query.filter(CreditCard.user_id==current_identity.id,
                                               CreditCard.is_active==True).first()
        return jsonify({"data": CardDetailsSerializer().dump(card_details).data})

    def put(self):
        data = ImmutableMultiDict(request.json)
        user = User.query.get(current_identity.id)
        credit_card_form = CreditCardForm(data, csrf_enabled=False)
        if credit_card_form.validate():
            credit_card = credit_card_form.save(instance=user)
            return jsonify({"status": "success", "data": CardDetailsSerializer().dump(credit_card).data})
        return credit_card_form.errors

    def delete(self):
        db.session.query(CreditCard).filter(CreditCard.user_id==current_identity.id,
                                            CreditCard.is_active==True).update({"is_active": False})
        db.session.commit()
        return '', 204


class MessageView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self):
        messages = Message.query.filter(Message.user==current_identity.id).all()
        return jsonify({"data": MessageSerializer().dump(messages, many=True).data})

    def post(self):
        abort_if_not_an_admin()
        data = ImmutableMultiDict(request.json)
        message_form = MessageForm(data, csrf_enabled=False)
        if message_form.validate():
            message_form.save()
            return {"status": "success"}
        return message_form.errors


class MessageDetailView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self, message_id):
        message = Message.query.get(message_id)
        abort_if_not_a_right_user(message.user)
        db.session.query(Message).filter(Message.id==message_id).update({"read": True})
        db.session.commit()
        return jsonify({"data": MessageSerializer().dump(message).data})


class ContactGroupView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self):
        groups = ContactGroup.query.filter(ContactGroup.owner==current_identity.id).all()
        return jsonify({"data": ContactGroupSerializer().dump(groups, many=True).data})

    def post(self):
        data = ImmutableMultiDict(request.json)
        create_group_form = CreateContactGroupForm(data, csrf_enabled=False)
        if create_group_form.validate():
            group = create_group_form.save()
            return jsonify({"status": "success", "data": ContactGroupSerializer().dump(group).data})
        return create_group_form.errors


class ContactGroupingView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def post(self):
        data = ImmutableMultiDict(request.json)
        contact_grouping_form = ContactGroupingForm(data, csrf_enabled=False)
        if contact_grouping_form.validate():
            group = contact_grouping_form.save()
            return jsonify({"status": "success", "data": ContactGroupSerializer().dump(group).data})
        return contact_grouping_form.errors

    def delete(self):
        data = ImmutableMultiDict(request.json)
        contact_grouping_form = ContactGroupingForm(data, csrf_enabled=False)
        if contact_grouping_form.validate():
            abort_if_not_a_right_owner(data['group'])
            contact_grouping_form.delete()
            return '', 204
        return contact_grouping_form.errors


class ContactGroupDetailView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self, group_id):
        group = ContactGroup.query.filter(ContactGroup.id==group_id).first()
        return jsonify({"data": ContactGroupSerializer().dump(group).data})

    def put(self, group_id):
        data = ImmutableMultiDict(request.json)
        contact_group_rename_form = ContactGroupRenameForm(data, csrf_enabled=False)
        if contact_group_rename_form.validate():
            instance = ContactGroup.query.filter(ContactGroup.id==group_id).first()
            group = contact_group_rename_form.save(instance)
            return jsonify({"status": "success", "data": ContactGroupSerializer().dump(group).data})
        return contact_group_rename_form.errors

    def delete(self, group_id):
        abort_if_not_a_right_owner(group_id)
        db.session.query(ContactGroup).filter(ContactGroup.id==group_id).delete()
        db.session.commit()
        return '', 204


class PlanDetailsView(Resource):
    method_decorators = [plan_not_expired(), jwt_required()]

    def get(self):
        plan = Plan.query.filter(Plan.user_id==current_identity.id).first()
        return jsonify({"data": PlanSerializer().dump(plan).data})
