from django.contrib import admin


from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Event, Ticket

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'enrollment_no', 'department', 'is_active', 'last_login')
    list_filter = ('role', 'department', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'enrollment_no')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'department', 'enrollment_no', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'department', 'enrollment_no', 'profile_image')}),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ['code']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'date', 'location', 'available_tickets', 'tickets_left')
    list_filter = ('department', 'date', 'category')
    search_fields = ('title', 'description', 'location')
    autocomplete_fields = ['department', 'created_by']
    ordering = ['-date']
    
    def tickets_left(self, obj):
        return obj.tickets_left()
    tickets_left.short_description = 'Tickets Left'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'booked_at')
    list_filter = ('event__department', 'booked_at')
    search_fields = ('user__username', 'user__enrollment_no', 'event__title')
    autocomplete_fields = ['user', 'event']
