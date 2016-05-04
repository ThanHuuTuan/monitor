__author__ = 'savad'
from flask import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from marshmallow import fields, Schema


class BaseUserSerializer(Schema):

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'username', 'email')


class UserSerializer(Schema):

    class Meta:
        fields = BaseUserSerializer.Meta.fields + ('phone', 'company', 'country', 'time_zone',
                                                   'website', 'industry', 'company_size', 'dst',
                                                   'logo_image_name', 'logo_image_path',
                                                   'permission_type', 'is_active',
                                                   'parent', 'is_admin',
                                                   'date_created', 'date_modified')


class ContactGroupSerializer(Schema):
    user = fields.Nested(BaseUserSerializer, many=True)

    class Meta:
        fields = ('id', 'name', 'user')


class MessageSerializer(Schema):

    class Meta:
        fields = ('id', 'subject', 'user', 'text', 'read', 'date_created')


class CardDetailsSerializer(Schema):

    class Meta:
        fields = ('id', 'card_holders_name', 'card_number', 'card_type', 'expiration_month',
                  'expiration_year', 'billing_company', 'billing_address', 'city', 'state',
                  'zip_code', 'country', 'stripe_customer_id', 'is_active', 'user_id')


class PlanSerializer(Schema):
    user = fields.Nested(BaseUserSerializer)

    class Meta:
        fields = ('id', 'plan_level', 'plan_period', 'plan_bought', 'plan_expires', 'plan_trial',
                  'plan_last_change', 'plan_price', 'user')
