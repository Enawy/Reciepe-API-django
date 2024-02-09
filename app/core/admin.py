from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class UserAdmin(BaseUserAdmin):
    # define the admin pages for users list will display the list items and fieldsets will display details of user
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # display main fields with no title
        (
            _('permissions'),  # displays permission title with those fields under it
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (  # classes wide only change the CSS of the page makes it look more responsive for certain fields
        (None, {'classes': ('wide',), 'fields': (
            'email',
            'password1',
            'password2',
            'name',
            'is_active',
            'is_staff',
            'is_superuser',
        )
                }
         ),
    )


admin.site.register(models.User, UserAdmin)
