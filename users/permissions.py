from django.db.models.aggregates import Sum, Count
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from companies.models import CompanyUser
from users.models import User


class UserLimit(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            company = request.user.active_company
            user = company.created_by

            users_count = CompanyUser.objects.filter(company__created_by=user).count()

            return users_count + 1 < user.max_users
        return True


class NotificationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            company = request.user.active_company
            user = company.created_by

            users_count = CompanyUser.objects.filter(company__created_by=user).count()

            return users_count + 1 < user.max_users
        return True
